from ..authentication import Authenticator
from ..logger import LoggerLike
from ..models.auth import AuthUserResponse, GetInfoResponse, LogoffResponse
from ..operations import operation
from ..runtime import Clock
from ..service_base import (
    RequestExecutor,
    SessionContext,
    SessionGate,
    SessionMutator,
    _BaseService,
)

LOGOFF = operation("logoff", LogoffResponse)
GET_INFO = operation("get_info", GetInfoResponse)


class AuthService(_BaseService):
    def __init__(
        self,
        request_executor: RequestExecutor,
        session_context: SessionContext,
        session_gate: SessionGate,
        session_mutator: SessionMutator,
        authenticator: Authenticator,
        clock: Clock,
        logger: LoggerLike,
    ) -> None:
        super().__init__(request_executor, session_context, session_gate, logger)
        self.__session_mutator = session_mutator
        self.__authenticator = authenticator
        self.__clock = clock

    async def logoff(
        self,
        *,
        api_version: str | None = None,
    ) -> LogoffResponse:
        """Завершить серверную сессию и очистить локальное состояние клиента.

        Вызывайте метод в ``finally`` или используйте контекстный менеджер
        ``APIClient``. Session ID не следует выводить в логи.
        """
        response = await self._request(LOGOFF, api_version=api_version)
        self.__session_mutator.reset()
        return response

    async def get_info(
        self,
        *,
        api_version: str | None = None,
        period: str | None = None,
    ) -> GetInfoResponse:
        """Получение статистических данных по вызовам всех методов."""
        if period is None:
            now = self.__clock.now()
            period = now.strftime("%Y-%m-%d %H:%M:%S")
        return await self._request(
            GET_INFO,
            api_version=api_version,
            params={"period": period},
        )

    async def auth_user(
        self,
        *,
        api_version: str | None = None,
        contract_id: str | None = None,
        contract_number: str | None = None,
    ) -> AuthUserResponse:
        """Авторизоваться и выбрать договор для последующих запросов.

        Типовой сценарий:
            Выполнить авторизацию в начале интеграционного сценария и сохранить
            только идентификатор выбранного договора. Session ID SDK хранит и
            обновляет самостоятельно.

        Пример вызова:
        ```python
        auth = await client.auth.auth_user(contract_number="TEST-001")
        contract_id = auth.data.contracts[0].id
        ```

        Payload формируется из ``CredentialsProvider`` и выбранного договора;
        логин, пароль и session ID не должны попадать в журналирование.
        """
        return await self.__authenticator.authenticate(
            api_version=api_version,
            contract_id=contract_id,
            contract_number=contract_number,
        )
