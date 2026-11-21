"""Общая основа сервисов: выбор договора, проверка параметров и отправка запроса.

Публичные асинхронные методы каждого сервиса автоматически оборачиваются
:func:`_with_request_validation` (через ``_BaseService.__init_subclass__``), поэтому
ошибки моделей запроса и сбои выбора договора везде выглядят одинаково.
"""

from __future__ import annotations

import functools
import inspect
import time
from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from contextlib import aclosing
from dataclasses import replace
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from .error_reporting import audit_contract_resolution_failure
from .errors import ContractSelectionError, RequestValidationError
from .logger import LoggerLike
from .modeling import ResponseModel, StrictRequestModel
from .operations import OperationSpec
from .protocols import (
    JsonRequestExecutor,
    RequestExecutor,
    SessionContext,
    SessionGate,
)
from .requests import FormData, JsonValue, PathParams, QueryParams, RequestOptions
from .sanitization import scrub
from .validation import require_identifier

ResponseT = TypeVar("ResponseT", bound=ResponseModel)
RequestModelT = TypeVar("RequestModelT", bound=BaseModel)
# Временный договор для проверки DTO до входа; на сервер он не уходит.
_UNRESOLVED_CONTRACT_ID = "unresolved-contract"
_MAX_LISTED_REQUEST_PROBLEMS = 3


def _request_model_names() -> Iterator[str]:
    """Перечислить имена всех моделей запроса: ``StrictRequestModel`` и её потомков.

    Обходит дерево наследников во время вызова, поэтому учитывает и модели,
    объявленные после импорта этого модуля.

    :return: Имена классов моделей запроса.
    """
    pending = [StrictRequestModel]
    while pending:
        model_type = pending.pop()
        yield model_type.__name__
        pending.extend(model_type.__subclasses__())


def _is_request_model_error(error: PydanticValidationError) -> bool:
    """Проверить, что ошибка Pydantic пришла из модели запроса, а не ответа.

    Pydantic пишет имя модели в ``error.title``; по нему и отличаем. Ошибку модели
    ответа выдавать за ошибку параметров нельзя: пользователь стал бы искать
    проблему в своих аргументах.

    :param error: Ошибка проверки Pydantic.
    :return: ``True``, если ``error.title`` — имя модели запроса.
    """
    # Ошибка модели ответа уже стала ResponseValidationError в исполнителе; сюда
    # она может попасть только из заглушек, и выдавать её за ошибку параметров нельзя.
    return error.title in set(_request_model_names())


def _request_validation_error(error: PydanticValidationError) -> RequestValidationError:
    """Превратить ошибку Pydantic модели запроса в ``RequestValidationError``.

    Текст: «Параметры запроса не прошли проверку: поле: причина; …». Показываются
    первые 3 проблемы и «и ещё N»; входные значения в текст не попадают, а сам текст
    проходит через :func:`~apisdkopti24.sanitization.scrub` и обрезается до 1000
    символов, чтобы секрет из аргумента не утёк в исключение или журнал.

    :param error: Ошибка проверки модели запроса.
    :return: Готовое исключение SDK (не поднимается здесь).
    """
    problems = [
        f"{'.'.join(str(part) for part in problem['loc']) or 'запрос'}: {problem['msg']}"
        for problem in error.errors(include_url=False, include_input=False)
    ]
    listed = "; ".join(problems[:_MAX_LISTED_REQUEST_PROBLEMS])
    remaining = len(problems) - _MAX_LISTED_REQUEST_PROBLEMS
    if remaining > 0:
        listed += f"; и ещё {remaining}"
    message = " ".join(scrub(f"Параметры запроса не прошли проверку: {listed}").split())
    return RequestValidationError(message[:1000])


class _ContractResolutionFailed(Exception):
    """Внутренний сигнал: договор не выбран, публичному методу нужно записать аудит.

    Пользователь этот класс не видит: декоратор публичного метода достаёт из него
    исходную ошибку и поднимает её.

    :ivar error: Исходная ошибка (``ContractSelectionError``, ``RequestValidationError``
        или ошибка входа).
    :ivar elapsed_seconds: Сколько длилась попытка выбрать договор, для аудита.
    """

    def __init__(self, error: Exception, elapsed_seconds: float) -> None:
        super().__init__()
        self.error = error
        self.elapsed_seconds = elapsed_seconds


def _audited_contract_error(
    service: _BaseService, method_name: str, failure: _ContractResolutionFailed
) -> Exception:
    """Записать в аудит сбой выбора договора и вернуть исходную ошибку.

    Вызывается декоратором публичного метода. Аудит пишется здесь, а не в
    ``_resolve_contract_id``, потому что только декоратор знает имя публичного
    метода, который вызвал пользователь.

    :param service: Сервис, из которого взят журнал.
    :param method_name: Имя публичного метода для события аудита.
    :param failure: Сигнал с исходной ошибкой и временем попытки.
    :return: Исходная ошибка; вызывающий код поднимает её с ``from None``, чтобы
        внутренний сигнал не попал в трассировку.
    """
    audit_contract_resolution_failure(
        method_name=method_name,
        error=failure.error,
        logger=service.logger,
        elapsed_seconds=failure.elapsed_seconds,
    )
    return failure.error


def _with_request_validation(method: Callable[..., Any]) -> Callable[..., Any]:
    """Обернуть публичный метод сервиса единой обработкой ошибок до запроса.

    Обёртка ловит два случая:

    * ``_ContractResolutionFailed`` — договор выбрать не удалось. Сбой пишется в
      аудит (:func:`_audited_contract_error`), пользователь получает исходную ошибку.
    * ``pydantic.ValidationError`` модели запроса — параметры неверны. Ошибка
      превращается в ``RequestValidationError`` (:func:`_request_validation_error`),
      исходная остаётся в ``__cause__``. Ошибки других моделей пробрасываются без
      изменений.

    Асинхронный генератор (методы ``iter_*``) оборачивается генератором и
    закрывается через ``aclosing`` даже при ошибке посреди перебора; обычная
    корутина — корутиной. ``functools.wraps`` сохраняет имя и докстроку метода
    для справочника. Вызывается из ``_BaseService.__init_subclass__``, вручную не
    применяется.

    :param method: Публичный асинхронный метод или асинхронный генератор сервиса.
    :return: Обёртка того же вида (корутина или асинхронный генератор).
    """
    if inspect.isasyncgenfunction(method):

        @functools.wraps(method)
        async def iterate(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
            """Обёртка асинхронного генератора: отдаёт элементы и переводит ошибки до запроса."""
            try:
                async with aclosing(method(*args, **kwargs)) as items:
                    async for item in items:
                        yield item
            except _ContractResolutionFailed as failure:
                raise _audited_contract_error(args[0], method.__name__, failure) from None
            except PydanticValidationError as error:
                if not _is_request_model_error(error):
                    raise
                raise _request_validation_error(error) from error

        return iterate

    @functools.wraps(method)
    async def call(*args: Any, **kwargs: Any) -> Any:
        """Обёртка корутины: возвращает результат метода и переводит ошибки до запроса."""
        try:
            return await method(*args, **kwargs)
        except _ContractResolutionFailed as failure:
            raise _audited_contract_error(args[0], method.__name__, failure) from None
        except PydanticValidationError as error:
            if not _is_request_model_error(error):
                raise
            raise _request_validation_error(error) from error

    return call


class _BaseService:
    """Основа сервисов JSON API: договор, проверка параметров, отправка запроса.

    Сервис не держит сетевого состояния: исполнитель, сессия и журнал приходят из
    клиента и общие для всех сервисов.

    :param request_executor: Исполнитель JSON-запросов (повторы, перелогин, аудит).
    :param session_context: Чтение текущей сессии: договор и список договоров логина.
    :param session_gate: Вход по требованию (``authUser``) перед выбором договора.
    :param logger: Журнал SDK с очисткой секретов.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Обернуть публичные асинхронные методы подкласса :func:`_with_request_validation`.

        Срабатывает при объявлении каждого сервиса. Методы с ``_`` в начале не
        оборачиваются: их ошибки обрабатывает публичный метод, который их вызвал.
        """
        super().__init_subclass__(**kwargs)
        for name, member in vars(cls).items():
            is_async = inspect.iscoroutinefunction(member) or inspect.isasyncgenfunction(member)
            if is_async and not name.startswith("_"):
                setattr(cls, name, _with_request_validation(member))

    def __init__(
        self,
        request_executor: JsonRequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        logger: LoggerLike,
    ) -> None:
        self.__request_executor = request_executor
        self.__session_context = session_context
        self.__session_gate = session_gate
        self.__logger = logger

    @property
    def logger(self) -> LoggerLike:
        """Журнал SDK, общий для клиента; секреты в нём уже маскируются."""
        return self.__logger

    @property
    def contract_id(self) -> str | None:
        """Договор текущей сессии или ``None``, если вход ещё не выполнялся. Без сети."""
        return self.__session_context.contract_id

    async def _resolve_contract_id(self, contract_id: str | None) -> str:
        """Выбрать договор запроса: явный ``contract_id`` или договор сессии.

        Явный договор только проверяется (непустая строка, пробелы по краям
        обрезаются), сети нет. Без него метод ждёт вход (authUser, если сессии ещё
        нет) и берёт договор сессии; при неудаче время попытки уходит в аудит.

        :param contract_id: Договор из аргумента публичного метода или ``None``.
        :return: Договор для query, тела и заголовка запроса.
        :raises RequestValidationError: Явный ``contract_id`` пустой.
        :raises _ContractResolutionFailed: Договор сессии выбрать не удалось. Внутри
            исходная ошибка (``ContractSelectionError``, ``RequestValidationError`` или
            ошибка входа); декоратор публичного метода пишет аудит и поднимает её.
        """
        if contract_id is not None:
            return require_identifier(contract_id, "contract_id")
        started_at = time.monotonic()
        try:
            return await self.__session_contract_id()
        except Exception as error:
            raise _ContractResolutionFailed(error, time.monotonic() - started_at) from error

    async def __session_contract_id(self) -> str:
        """Войти при необходимости и вернуть договор сессии.

        :return: Договор по умолчанию или выбранный через ``client.select_contract()``.
        :raises ContractSelectionError: Договор не выбран, а у логина их несколько; в ошибке
            список ``available_contracts``.
        :raises RequestValidationError: Договор не выбран и выбрать его не из чего.
        """
        # Сначала вход: список договоров логина и договор по умолчанию становятся
        # известны только из ответа authUser.
        await self.__session_gate.ensure_authenticated()
        if self.__session_context.contract_id is None:
            choices = self.__session_context.available_contracts
            if len(choices) > 1:
                raise ContractSelectionError(
                    "Доступно несколько договоров: передайте contract_id в метод или "
                    "выберите договор через client.select_contract()",
                    available_contracts=choices,
                )
            raise RequestValidationError(
                "Необходимо указать contract_id, если договор по умолчанию не выбран"
            )
        return require_identifier(self.__session_context.contract_id, "contract_id")

    async def _validated_with_contract(
        self,
        model_type: type[RequestModelT],
        contract_id: str | None,
        fields: dict[str, Any],
    ) -> tuple[str, RequestModelT]:
        """Проверить модель запроса до входа, затем выбрать договор и подставить его.

        Общий шаг методов, у которых модель запроса содержит ``contract_id``. Порядок
        важен: выбор договора без явного ``contract_id`` может выполнить вход
        (authUser) и занять слот ограничителя частоты, а ошибка в аргументах не
        должна стоить ни того, ни другого. Поэтому:

        1. ``model_type`` проверяется по ``fields``. Если ``contract_id`` не передан,
           вместо него стоит временное ``_UNRESOLVED_CONTRACT_ID``; на сервер оно
           не уходит.
        2. ``_resolve_contract_id`` выбирает договор: явный или договор сессии.
        3. В копию модели подставляется выбранный договор. ``model_copy`` не проверяет
           значение заново; это безопасно, договор уже прошёл ``require_identifier``.

        Порядок закреплён тестом ``tests/test_validation_order.py``.

        :param model_type: Строгая модель запроса с полем ``contract_id``.
        :param contract_id: Договор из аргумента публичного метода или ``None``.
        :param fields: Остальные поля модели, без ``contract_id``.
        :return: Пара ``(contract_id, model)``: выбранный договор и проверенная модель
            с этим договором.
        :raises pydantic.ValidationError: ``fields`` не прошли модель. Декоратор
            публичного метода превращает её в ``RequestValidationError``.
        :raises RequestValidationError: Явный ``contract_id`` пустой.
        :raises _ContractResolutionFailed: Договор сессии выбрать не удалось (вход
            упал, договоров несколько или ни одного). Декоратор публичного метода
            пишет аудит и поднимает исходную ошибку.
        """
        # Шаг 1, до сети. Пустая строка тоже заменяется временным договором: модель
        # проверяет остальные поля, а пустой договор отклонит шаг 2.
        draft = model_type.model_validate(
            {**fields, "contract_id": contract_id or _UNRESOLVED_CONTRACT_ID}
        )
        # Шаг 2: без явного договора здесь может выполниться вход (authUser).
        cid = await self._resolve_contract_id(contract_id)
        # Шаг 3: model_copy не проверяет cid заново, он уже прошёл require_identifier.
        return cid, draft.model_copy(update={"contract_id": cid})

    async def _resolve_batch_contract_id(
        self,
        *,
        contract_id: str | None,
        item_contract_ids: Sequence[str | None],
    ) -> str:
        """Выбрать один договор для пакета и отклонить элементы с разными договорами.

        API принимает пакет (например, лимиты в ``set_limit``) только в рамках одного
        договора. Порядок выбора: явный ``contract_id``; иначе общий договор
        элементов; иначе договор сессии через ``_resolve_contract_id``. Сеть нужна
        только в последнем случае.

        :param contract_id: Договор из аргумента публичного метода или ``None``.
        :param item_contract_ids: Договоры элементов пакета; ``None`` у элемента
            значит «как у пакета».
        :return: Договор, который получат все элементы и заголовок запроса.
        :raises RequestValidationError: Пустой договор; договор элемента не совпадает с
            явным; у элементов разные договоры.
        :raises _ContractResolutionFailed: Договор сессии выбрать не удалось.
        """
        normalized_explicit = (
            require_identifier(contract_id, "contract_id") if contract_id is not None else None
        )
        normalized_items = {
            require_identifier(item_contract_id, "contract_id")
            for item_contract_id in item_contract_ids
            if item_contract_id is not None
        }
        if normalized_explicit is not None:
            conflicting = normalized_items - {normalized_explicit}
            if conflicting:
                raise RequestValidationError(
                    "contract_id элементов пакета должен совпадать с contract_id запроса"
                )
            return normalized_explicit
        if len(normalized_items) > 1:
            raise RequestValidationError("Все элементы пакета должны иметь одинаковый contract_id")
        if normalized_items:
            return next(iter(normalized_items))
        return await self._resolve_contract_id(None)

    @staticmethod
    def _build_request_options(
        *,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
        form: FormData | None = None,
        json_body: JsonValue = None,
    ) -> RequestOptions:
        """Собрать ``RequestOptions``: куда положить параметры одного запроса.

        ``contract_header`` уходит в заголовок ``contract_id``. Пустые части
        заменяются пустыми словарями, чтобы исполнитель не проверял ``None``.
        """
        return RequestOptions(
            route_name=route_name,
            path_params=path_params or {},
            contract_id=contract_header,
            query=query or {},
            form=form,
            json_body=json_body,
        )

    async def _request(
        self,
        operation: OperationSpec[ResponseT],
        *,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
        form: FormData | None = None,
        json_body: JsonValue = None,
        recover_session: bool = True,
    ) -> ResponseT:
        """Отправить операцию через исполнитель и вернуть проверенную модель ответа.

        Единая точка выхода сервисов в сеть. Маршрут, таймаут, повторы и разбор
        ответа берутся из ``operation``; исполнитель добавляет сессию, аудит и один
        повторный вход при истёкшей сессии.

        :param operation: Описание операции из ``operation(...)``.
        :param route_name: Вариант маршрута операции, например ``post_override``.
        :param path_params: Значения для подстановки в путь.
        :param contract_header: Договор для заголовка ``contract_id`` или ``None``.
        :param query: Параметры строки запроса.
        :param form: Поля формы; несовместимо с ``json_body``.
        :param json_body: Тело JSON; несовместимо с ``form``.
        :param recover_session: ``False`` запрещает повторный вход при 401, например
            для ``logoff``.
        :return: Модель ответа типа ``operation``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа.
        """
        options = self._build_request_options(
            route_name=route_name,
            path_params=path_params,
            contract_header=contract_header,
            query=query,
            form=form,
            json_body=json_body,
        )
        if not recover_session:
            options = replace(options, recover_session=False)
        return await self.__request_executor.execute(operation, options=options)


class _StreamingService(_BaseService):
    """Основа сервисов, которые скачивают файлы (отчёты, документы).

    Добавляет к :class:`_BaseService` скачивание в память и потоковую запись на
    диск; исполнитель должен уметь и JSON, и байты, и файлы.

    :param request_executor: Исполнитель JSON, байтов и файлов.
    :param session_context: Чтение текущей сессии.
    :param session_gate: Вход по требованию.
    :param logger: Журнал SDK.
    """

    def __init__(
        self,
        request_executor: RequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        logger: LoggerLike,
    ) -> None:
        super().__init__(request_executor, session_context, session_gate, logger)
        self.__stream_executor = request_executor

    async def _request_stream(
        self,
        operation: OperationSpec[bytes],
        *,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
    ) -> bytes:
        """Скачать файл операции в память (без разбора JSON).

        Параметры как у ``_request``. Подходит для небольших отчётов; большой
        файл лучше писать на диск через ``_request_stream_to_file``.
        """
        return await self.__stream_executor.execute_stream(
            operation,
            options=self._build_request_options(
                route_name=route_name,
                path_params=path_params,
                contract_header=contract_header,
                query=query,
            ),
        )

    async def _request_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        *,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
    ) -> Path:
        """Потоково записать файл операции в ``destination`` и вернуть путь.

        Параметры как у ``_request``; файл пишется частями, не целиком в памяти.
        """
        return await self.__stream_executor.execute_stream_to_file(
            operation,
            destination,
            options=self._build_request_options(
                route_name=route_name,
                path_params=path_params,
                contract_header=contract_header,
                query=query,
            ),
        )
