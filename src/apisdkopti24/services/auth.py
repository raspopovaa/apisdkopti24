from ..authentication import Authenticator
from ..errors import NotAuthenticatedError
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
    ) -> LogoffResponse | None:
        """Завершить серверную сессию и очистить локальное состояние клиента.

        Вызывайте метод явно, когда нужно завершить серверную сессию.
        Контекстный менеджер ``APIClient`` закрывает локальные ресурсы, но не
        заменяет серверный logoff. Session ID не следует выводить в логи.

        Без активной сессии запрос не отправляется: метод очищает локальное
        состояние и возвращает ``None``. Иначе обычный путь запроса сначала
        выполнил бы authUser, чтобы сразу закрыть только что открытую сессию.
        По той же причине ответ ``401`` (сессия на сервере уже истекла) не
        запускает повторный вход: сессия считается завершённой, метод
        возвращает ``None``.
        """
        if self.__session_mutator.session_id is None:
            self.__session_mutator.reset()
            return None
        try:
            return await self._request(LOGOFF, api_version=api_version, recover_session=False)
        except NotAuthenticatedError:
            return None
        finally:
            self.__session_mutator.reset()

    async def get_info(
        self,
        *,
        api_version: str | None = None,
        period: str | None = None,
    ) -> GetInfoResponse:
        """Получить статистику вызовов методов и сведения о тарифе.

        ``period`` — месяц ``YYYY-MM`` или день ``YYYY-MM-DD``. Без ``period`` SDK
        запрашивает текущий месяц по часам клиента. Значение с временем
        (``YYYY-MM-DD HH:MM:SS``) сервер понимает как начало окна в 24 часа
        вперёд от этого момента.
        """
        if period is None:
            period = self.__clock.now().strftime("%Y-%m")
        return await self._request(
            GET_INFO,
            api_version=api_version,
            query={"period": period},
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
