"""Исполнители запросов: подготовка по ``OperationSpec``, вход, перелогин и аудит.

:class:`OperationExecutor` собирает запрос (маршрут, заголовки, таймауты,
бюджет) и разбирает ответ. :class:`DefaultRequestExecutor` оборачивает его:
входит перед запросом, один раз перелогинивается, если сервер отклонил
сессию, и пишет события аудита.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Protocol, TypeVar

from pydantic import ValidationError as PydanticValidationError

from .config import TimeoutPolicy
from .error_reporting import OperationAudit
from .errors import (
    CLIENT_CLOSED_MESSAGE,
    NotAuthenticatedError,
    RequestPreparationError,
    ResponseShapeError,
    ResponseValidationError,
    SDKConfigurationError,
)
from .execution_budget import OperationBudget
from .logger import LoggerLike
from .modeling import ResponseModel, decode_model
from .operations import OperationSpec
from .protocols import APIKeyProvider, SessionContext, SessionGate, SessionRecovery
from .requests import FileTarget, PreparedRequest, RequestOptions
from .runtime import Clock
from .sanitization import REDACTED, is_sensitive_log_key, sanitize_for_logging

ResponseT = TypeVar("ResponseT", bound=ResponseModel)
ResultT = TypeVar("ResultT")
# HTTP 401 с другим типом в теле (accessDenied) вход заново не исправит.
_SESSION_EXPIRED_ERROR_TYPES = frozenset({None, "notAuthenticated"})


class JsonTransport(Protocol):
    """Транспорт, который отправляет запрос и возвращает разобранный JSON."""

    async def request(self, request: PreparedRequest) -> dict[str, object]:
        """Отправить запрос (с повторами транспорта) и вернуть тело ответа как словарь."""
        ...


class BytesTransport(Protocol):
    """Транспорт, который скачивает ответ в память."""

    async def request_stream(self, request: PreparedRequest) -> bytes:
        """Отправить запрос и вернуть тело ответа байтами (с ограничением размера)."""
        ...


class FileTransport(Protocol):
    """Транспорт, который потоково пишет ответ в файл."""

    async def request_stream_to_file(
        self,
        request: PreparedRequest,
        target: FileTarget,
    ) -> Path:
        """Отправить запрос и записать тело ответа в файл; вернуть путь к нему."""
        ...


class Transport(JsonTransport, BytesTransport, FileTransport, Protocol):
    """Полный транспорт: JSON, байты, файл и закрытие соединений."""

    async def aclose(self) -> None:
        """Закрыть HTTP-соединения транспорта."""
        ...


class OperationExecutor:
    """Подготовить запросы по OperationSpec независимо от реализации транспорта."""

    def __init__(
        self,
        *,
        api_key_provider: APIKeyProvider,
        transport: Transport,
        session_context: SessionContext,
        timeouts: TimeoutPolicy,
        logger: LoggerLike,
        clock: Clock,
        max_attempts: int = 5,
    ) -> None:
        if max_attempts < 1:
            raise SDKConfigurationError("max_attempts должен быть не меньше 1")
        self._api_key_provider = api_key_provider
        self._transport = transport
        self._session_context = session_context
        self._timeouts = timeouts
        self._logger = logger
        self._clock = clock
        self._max_attempts = max_attempts
        self._closed = False

    def close(self) -> None:
        """Пометить исполнитель закрытым: новые запросы будут отклонены."""
        self._closed = True

    def ensure_open(self) -> None:
        """Проверить, что клиент не закрыт.

        :raises SDKConfigurationError: Клиент закрыт.
        """
        if self._closed:
            raise SDKConfigurationError(CLIENT_CLOSED_MESSAGE)

    def build_headers(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
    ) -> dict[str, str]:
        """Собрать заголовки запроса: ключ API, время, сессия и договор.

        Ключ API читается у поставщика при каждом запросе, поэтому ротация ключа
        действует сразу. ``session_id`` и заголовок ``contract_id`` добавляются только
        операциям, которым они нужны по каталогу. Пользовательские заголовки не могут
        переопределить служебные (``api_key``, ``session_id``, ``contract_id``,
        ``date_time``). В журнал DEBUG заголовки попадают очищенными.

        :param operation: Описание операции.
        :param options: Параметры запроса.
        :return: Словарь заголовков.
        :raises RequestPreparationError: Поставщик вернул пустой ключ или переопределяется
            служебный заголовок.
        """
        api_key = self._api_key_provider.get_api_key()
        if not api_key:
            raise RequestPreparationError("Поставщик ключа API вернул пустое значение")
        context = self._session_context.request_context(contract_id=options.contract_id)
        headers: dict[str, str] = {
            "api_key": api_key,
            "date_time": self._clock.now().strftime("%Y-%m-%d %H:%M:%S"),
            "User-Agent": "apisdkopti24",
        }
        if options.json_body is not None:
            headers["Content-Type"] = "application/json"
        elif options.form is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if operation.requires_session and context.session_id:
            headers["session_id"] = context.session_id
            if context.contract_id and "header" in operation.request.contract_locations:
                headers["contract_id"] = context.contract_id
        protected = {"api_key", "session_id", "contract_id", "date_time", "content_type"}
        for name, value in options.headers.items():
            if name.lower().replace("-", "_") in protected:
                raise RequestPreparationError(f"Переопределение заголовка запрещено: {name}")
            headers[name] = value
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Подготовленные заголовки: %s", sanitize_for_logging(headers))
        return headers

    def prepare(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
        budget: OperationBudget,
    ) -> PreparedRequest:
        """Подготовить запрос по описанию операции.

        Сверяет параметры с каталогом: строка запроса, форма, JSON и заголовок
        договора допустимы, только если операция их принимает. Так ошибка в сервисе
        обнаруживается до отправки.

        :param operation: Описание операции.
        :param options: Параметры запроса.
        :param budget: Бюджет операции.
        :return: Готовый запрос для транспорта.
        :raises SDKConfigurationError: Клиент закрыт.
        :raises RequestPreparationError: Параметр в месте, которое операция не принимает.
        """
        self.ensure_open()
        request_spec = operation.request
        if options.query and not request_spec.has_query:
            raise RequestPreparationError(
                f"Операция {operation.name!r} не принимает параметры строки запроса"
            )
        if options.form is not None and request_spec.body_kind != "form":
            raise RequestPreparationError(f"Операция {operation.name!r} не принимает данные формы")
        if options.json_body is not None and request_spec.body_kind != "json":
            raise RequestPreparationError(f"Операция {operation.name!r} не принимает тело JSON")
        if options.contract_id is not None and "header" not in request_spec.contract_locations:
            raise RequestPreparationError(
                f"Операция {operation.name!r} не принимает заголовок contract_id"
            )
        route = operation.resolve_route(route_name=options.route_name)
        context = self._session_context.request_context(contract_id=options.contract_id)
        return PreparedRequest(
            method=route.http_method,
            endpoint=route.render(options.path_params),
            api_version=route.api_version,
            headers=self.build_headers(operation, options),
            query=options.query,
            form=options.form,
            json_body=options.json_body,
            timeout=self._timeouts.resolve(operation.timeout_class),
            method_name=operation.name,
            retry_class=operation.retry_class,
            idempotent=operation.idempotent,
            request_context=context,
            operation_budget=budget,
            connect_timeout=self._timeouts.connect,
            billable=bool(route.billable if route.billable is not None else operation.billable),
        )

    def create_budget(self, operation: OperationSpec[object]) -> OperationBudget:
        """Создать бюджет операции: срок по классу таймаута и предел попыток клиента.

        :param operation: Описание операции.
        :return: Новый бюджет.
        """
        return OperationBudget(
            deadline_at=self._clock.monotonic()
            + self._timeouts.resolve_total(operation.timeout_class),
            max_attempts=self._max_attempts,
        )

    @property
    def clock(self) -> Clock:
        """Часы клиента."""
        return self._clock

    @property
    def session_context(self) -> SessionContext:
        """Чтение текущей сессии клиента."""
        return self._session_context

    @staticmethod
    def decode_response(
        operation: OperationSpec[ResponseT],
        payload: dict[str, object],
    ) -> ResponseT:
        """Проверить JSON ответа моделью операции.

        :param operation: Описание операции с типом ответа.
        :param payload: Разобранное тело ответа.
        :return: Модель ответа.
        :raises ResponseShapeError: У операции нет типа ответа.
        :raises ResponseValidationError: Ответ не совпал с моделью.
        """
        if operation.response_type is None:
            raise ResponseShapeError(f"Операция JSON {operation.name!r} не содержит типа ответа")
        try:
            return decode_model(operation.response_type, payload)
        except PydanticValidationError as exc:
            raise ResponseValidationError.from_pydantic(
                exc,
                operation=operation.name,
                model_name=operation.response_type.__name__,
            ) from exc

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
        *,
        budget: OperationBudget | None = None,
    ) -> ResponseT:
        """Подготовить, отправить и разобрать запрос без входа, перелогина и аудита.

        Используется для ``authUser``: вход не должен сам вызывать вход.

        :param operation: Описание операции.
        :param options: Параметры запроса.
        :param budget: Бюджет операции; без него создаётся новый.
        :return: Модель ответа.
        """
        request_options = options or RequestOptions()
        prepared = self.prepare(
            operation,
            request_options,
            budget or self.create_budget(operation),
        )
        payload = await self._transport.request(prepared)
        return self.decode_response(operation, payload)

    async def send_json(self, request: PreparedRequest) -> dict[str, object]:
        """Отправить подготовленный запрос и вернуть JSON ответа."""
        return await self._transport.request(request)

    async def send_bytes(self, request: PreparedRequest) -> bytes:
        """Отправить подготовленный запрос и вернуть тело ответа байтами."""
        return await self._transport.request_stream(request)

    async def send_file(self, request: PreparedRequest, target: FileTarget) -> Path:
        """Отправить подготовленный запрос и записать ответ в файл."""
        return await self._transport.request_stream_to_file(request, target)


class _AttemptSession:
    """session_id, с которым был отправлен последний запрос операции."""

    __slots__ = ("session_id", "sent", "recover_session")

    def __init__(self, *, recover_session: bool = True) -> None:
        """Начать без отправленного запроса.

        :param recover_session: Разрешён ли перелогин для этой операции.
        """
        self.session_id: str | None = None
        self.sent = False
        self.recover_session = recover_session


class DefaultRequestExecutor:
    """Проверить и восстановить сессию, записать аудит и разобрать типизированный ответ.

    :param operation_executor: Подготовка и отправка запросов.
    :param session_gate: Вход перед запросом.
    :param session_recovery: Перелогин после отказа сервера в сессии.
    :param logger: Журнал аудита.
    :param clock: Часы; по умолчанию часы исполнителя операций.
    """

    def __init__(
        self,
        *,
        operation_executor: OperationExecutor,
        session_gate: SessionGate,
        session_recovery: SessionRecovery,
        logger: LoggerLike,
        clock: Clock | None = None,
    ) -> None:
        self._operations = operation_executor
        self._session_gate = session_gate
        self._session_recovery = session_recovery
        self._logger = logger
        self._clock = clock or operation_executor.clock

    def close(self) -> None:
        """Запретить новые операции: закрытый клиент не входит заново и не пишет аудит."""
        self._operations.close()

    def preview_headers(
        self,
        operation: OperationSpec[object],
        options: RequestOptions | None = None,
    ) -> dict[str, str]:
        """Подготовить очищенные заголовки для диагностики без раскрытия секретов."""
        headers = self._operations.build_headers(operation, options or RequestOptions())
        return {
            name: REDACTED if is_sensitive_log_key(name) else value
            for name, value in headers.items()
        }

    async def _run_with_recovery(
        self,
        operation: OperationSpec[object],
        request: Callable[[], Awaitable[ResultT]],
        budget: OperationBudget,
        audit: OperationAudit,
        attempt_session: _AttemptSession,
    ) -> ResultT:
        """Выполнить запрос, при отказе в сессии перелогиниться и повторить один раз.

        Перелогин выполняется, только если все условия верны: операции нужна сессия,
        запрос действительно ушёл (иначе 401 пришёл от самого входа, и второй вход
        дал бы тот же отказ), перелогин разрешён параметрами и тип ошибки
        ``notAuthenticated`` или пустой (``accessDenied`` вход не исправит). Если сессию
        уже обновил параллельный запрос, повторяется только запрос, без входа. Аудит
        получает ровно одно завершающее событие, с ``recovered=True`` после перелогина.

        :param operation: Описание операции.
        :param request: Подготовка и отправка одной попытки.
        :param budget: Бюджет операции.
        :param audit: Аудит операции.
        :param attempt_session: С какой сессией ушёл запрос.
        :return: Результат запроса.
        """
        audit.start()
        try:
            result = await request()
        except NotAuthenticatedError as error:
            # 401 до отправки запроса пришёл от самой авторизации (authUser отклонил
            # учётные данные): повторный вход дал бы тот же отказ и второй authUser.
            if (
                not operation.requires_session
                or not attempt_session.sent
                or not attempt_session.recover_session
                or error.context.error_type not in _SESSION_EXPIRED_ERROR_TYPES
            ):
                audit.failed(error, budget)
                raise
            audit.event("session_recovery")
            try:
                if not self._session_refreshed_since(attempt_session):
                    await self._session_recovery.recover(budget)
                result = await request()
            except asyncio.CancelledError as error:
                audit.cancelled(error, budget, recovered=True)
                raise
            except Exception as error:
                audit.failed(error, budget, recovered=True)
                raise
            audit.completed(budget, recovered=True)
            return result
        except asyncio.CancelledError as error:
            audit.cancelled(error, budget)
            raise
        except Exception as error:
            audit.failed(error, budget)
            raise
        audit.completed(budget)
        return result

    def _session_refreshed_since(self, attempt_session: _AttemptSession) -> bool:
        """Проверить, обновил ли сессию другой запрос после отправки упавшего.

        Ответ 401 может прийти после того, как параллельный запрос уже восстановил
        сессию. Повторная авторизация тогда лишняя: она сбросила бы свежую сессию.
        Проверка и вызов recover() выполняются без await между ними, поэтому
        другая корутина не может вклиниться.
        """
        current_session_id = self._operations.session_context.session_id
        return current_session_id is not None and current_session_id != attempt_session.session_id

    async def _prepared(
        self,
        operation: OperationSpec[object],
        options: RequestOptions,
        budget: OperationBudget,
        attempt_session: _AttemptSession,
    ) -> PreparedRequest:
        """Войти при необходимости и подготовить запрос, запомнив его сессию.

        Параметры пути проверяются до входа: небезопасный идентификатор не должен
        стоить лишнего ``authUser``.

        :return: Подготовленный запрос.
        """
        # Параметры пути проверяются до входа: небезопасный идентификатор не должен
        # стоить лишнего authUser.
        operation.resolve_route(route_name=options.route_name).render(options.path_params)
        if operation.requires_session:
            await self._session_gate.ensure_authenticated(budget)
        prepared = self._operations.prepare(operation, options, budget)
        attempt_session.session_id = prepared.request_context.session_id
        attempt_session.sent = True
        return prepared

    async def _execute_with(
        self,
        operation: OperationSpec[Any],
        options: RequestOptions | None,
        send: Callable[[PreparedRequest], Awaitable[ResultT]],
    ) -> ResultT:
        """Один путь для JSON, байтов и файла: бюджет, аудит, вход и восстановление."""
        self._operations.ensure_open()
        request_options = options or RequestOptions()
        budget = self._operations.create_budget(operation)
        audit = OperationAudit(
            operation=operation,
            logger=self._logger,
            clock=self._clock,
            route_name=request_options.route_name,
        )
        attempt_session = _AttemptSession(recover_session=request_options.recover_session)

        async def request() -> ResultT:
            prepared = await self._prepared(operation, request_options, budget, attempt_session)
            return await send(prepared)

        return await self._run_with_recovery(operation, request, budget, audit, attempt_session)

    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
    ) -> ResponseT:
        """Выполнить JSON-операцию с входом, перелогином и аудитом.

        :param operation: Описание операции.
        :param options: Параметры запроса.
        :return: Проверенная модель ответа.
        """

        async def send(prepared: PreparedRequest) -> ResponseT:
            payload = await self._operations.send_json(prepared)
            return self._operations.decode_response(operation, payload)

        return await self._execute_with(operation, options, send)

    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes:
        """Скачать файл операции в память с входом, перелогином и аудитом.

        :param operation: Описание операции.
        :param options: Параметры запроса.
        :return: Тело ответа байтами.
        """
        return await self._execute_with(operation, options, self._operations.send_bytes)

    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path:
        """Потоково записать файл операции на диск с входом, перелогином и аудитом.

        :param operation: Описание операции.
        :param destination: Путь файла.
        :param options: Параметры запроса.
        :return: Путь записанного файла.
        """
        target = FileTarget(Path(destination))

        async def send(prepared: PreparedRequest) -> Path:
            return await self._operations.send_file(prepared, target)

        return await self._execute_with(operation, options, send)


__all__ = [
    "BytesTransport",
    "DefaultRequestExecutor",
    "FileTransport",
    "JsonTransport",
    "OperationExecutor",
    "Transport",
]
