from __future__ import annotations

import functools
import inspect
from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from contextlib import aclosing
from dataclasses import replace
from pathlib import Path
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from .errors import ContractSelectionError, RequestValidationError
from .execution_budget import OperationBudget
from .logger import LoggerLike
from .modeling import ResponseModel, StrictRequestModel
from .operations import OperationSpec
from .requests import FormData, JsonValue, PathParams, QueryParams, RequestOptions
from .sanitization import scrub
from .session import RequestContext, SessionSnapshot
from .validation import require_identifier

ResponseT = TypeVar("ResponseT", bound=ResponseModel)
RequestModelT = TypeVar("RequestModelT", bound=BaseModel)
# Временный договор для проверки DTO до входа; на сервер он не уходит.
_UNRESOLVED_CONTRACT_ID = "unresolved-contract"
_MAX_LISTED_REQUEST_PROBLEMS = 3


def _request_model_names() -> Iterator[str]:
    pending = [StrictRequestModel]
    while pending:
        model_type = pending.pop()
        yield model_type.__name__
        pending.extend(model_type.__subclasses__())


def _is_request_model_error(error: PydanticValidationError) -> bool:
    # Ошибка модели ответа уже стала ResponseValidationError в исполнителе; сюда
    # она может попасть только из заглушек, и выдавать её за ошибку параметров нельзя.
    return error.title in set(_request_model_names())


def _request_validation_error(error: PydanticValidationError) -> RequestValidationError:
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


def _with_request_validation(method: Callable[..., Any]) -> Callable[..., Any]:
    """Выдать ошибку DTO запроса из публичного метода как ``RequestValidationError``."""
    if inspect.isasyncgenfunction(method):

        @functools.wraps(method)
        async def iterate(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
            try:
                async with aclosing(method(*args, **kwargs)) as items:
                    async for item in items:
                        yield item
            except PydanticValidationError as error:
                if not _is_request_model_error(error):
                    raise
                raise _request_validation_error(error) from error

        return iterate

    @functools.wraps(method)
    async def call(*args: Any, **kwargs: Any) -> Any:
        try:
            return await method(*args, **kwargs)
        except PydanticValidationError as error:
            if not _is_request_model_error(error):
                raise
            raise _request_validation_error(error) from error

    return call


class JsonRequestExecutor(Protocol):
    async def execute(
        self,
        operation: OperationSpec[ResponseT],
        options: RequestOptions | None = None,
    ) -> ResponseT: ...


class BytesRequestExecutor(Protocol):
    async def execute_stream(
        self,
        operation: OperationSpec[bytes],
        options: RequestOptions | None = None,
    ) -> bytes: ...


class FileRequestExecutor(Protocol):
    async def execute_stream_to_file(
        self,
        operation: OperationSpec[bytes],
        destination: str | Path,
        options: RequestOptions | None = None,
    ) -> Path: ...


class RequestExecutor(
    JsonRequestExecutor,
    BytesRequestExecutor,
    FileRequestExecutor,
    Protocol,
):
    """Полный интерфейс исполнителя для сервисов, использующих все виды ответов."""


class SessionContext(Protocol):
    @property
    def session_id(self) -> str | None: ...

    @property
    def contract_id(self) -> str | None: ...

    def snapshot(self) -> SessionSnapshot: ...

    def request_context(self, *, contract_id: str | None = None) -> RequestContext: ...


class SessionGate(Protocol):
    async def ensure_authenticated(self) -> str: ...


class SessionRecovery(Protocol):
    async def recover(self, budget: OperationBudget) -> str: ...


class SessionMutator(SessionContext, Protocol):
    def mark_authenticated(
        self,
        session_id: str,
        contract_id: str | None = None,
    ) -> None: ...

    def set_contract(self, contract_id: str | None) -> None: ...

    def invalidate(self) -> None: ...

    def reset(self) -> None: ...


class CredentialsProvider(Protocol):
    def get_credentials(self) -> tuple[str, str]: ...


class APIKeyProvider(Protocol):
    def get_api_key(self) -> str: ...


class _BaseService:
    def __init_subclass__(cls, **kwargs: Any) -> None:
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
        return self.__logger

    @property
    def contract_id(self) -> str | None:
        return self.__session_context.contract_id

    async def _resolve_contract_id(self, contract_id: str | None) -> str:
        if contract_id is not None:
            return require_identifier(contract_id, "contract_id")
        await self.__session_gate.ensure_authenticated()
        if self.__session_context.contract_id is None:
            # available_contracts есть у SessionManager, но не в публичном протоколе
            # SessionContext: сторонние реализации контекста его не обязаны давать.
            choices = getattr(self.__session_context, "available_contracts", ())
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
        """Проверить DTO до входа, затем подставить договор сессии.

        Без явного ``contract_id`` договор известен только после authUser; ошибка в
        остальных полях не должна стоить входа, поэтому модель проверяется раньше.
        """
        draft = model_type.model_validate(
            {**fields, "contract_id": contract_id or _UNRESOLVED_CONTRACT_ID}
        )
        cid = await self._resolve_contract_id(contract_id)
        return cid, draft.model_copy(update={"contract_id": cid})

    async def _resolve_batch_contract_id(
        self,
        *,
        contract_id: str | None,
        item_contract_ids: Sequence[str | None],
    ) -> str:
        """Выбрать один договор для пакета и отклонить элементы с разными договорами."""
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
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
        form: FormData | None = None,
        json_body: JsonValue = None,
    ) -> RequestOptions:
        return RequestOptions(
            api_version=api_version,
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
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
        form: FormData | None = None,
        json_body: JsonValue = None,
        recover_session: bool = True,
    ) -> ResponseT:
        options = self._build_request_options(
            api_version=api_version,
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
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
    ) -> bytes:
        return await self.__stream_executor.execute_stream(
            operation,
            options=self._build_request_options(
                api_version=api_version,
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
        api_version: str | None = None,
        route_name: str = "default",
        path_params: PathParams | None = None,
        contract_header: str | None = None,
        query: QueryParams | None = None,
    ) -> Path:
        return await self.__stream_executor.execute_stream_to_file(
            operation,
            destination,
            options=self._build_request_options(
                api_version=api_version,
                route_name=route_name,
                path_params=path_params,
                contract_header=contract_header,
                query=query,
            ),
        )
