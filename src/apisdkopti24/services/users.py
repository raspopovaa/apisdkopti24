from collections.abc import AsyncIterator, Mapping

from ..errors import RequestValidationError
from ..models.users import (
    UserAttachContractRequest,
    UserBoolResponse,
    UserCardRequest,
    UserContractsRequest,
    UserCreateRequest,
    UserCreateResponse,
    UserFilter,
    UserItem,
    UserListResponse,
    UsersQuery,
)
from ..operations import operation
from ..payloads import with_method_override
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import (
    require_identifier,
    validate_identifier_list,
    validate_mobile,
    validate_positive_count,
    validate_sort_fields,
)

GET_USERS = operation("get_users", UserListResponse)
CREATE_USER = operation("create_user", UserCreateResponse)
ATTACH_CONTRACTS = operation("attach_contracts", UserBoolResponse)
DETACH_CONTRACTS = operation("detach_contracts", UserBoolResponse)
ATTACH_CARD = operation("attach_card", UserBoolResponse)
DETACH_CARD = operation("detach_card", UserBoolResponse)
DELETE_USER = operation("delete_user", UserBoolResponse)


class UsersService(_BaseService):
    """Методы работы с пользователями (v2)."""

    async def get_users(
        self,
        *,
        sort: str | None = None,
        page: int | None = None,
        on_page: int | None = None,
        q: str | None = None,
        filter: UserFilter | Mapping[str, object] | None = None,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> UserListResponse:
        """Получить страницу пользователей корпоративного клиента.

        ``q`` ищет по фамилии, имени, отчеству, логину, email и мобильному телефону.
        ``filter`` — ``role`` (``Supervisor``, ``Regulatory``, ``Driver`` или
        ``Readonly``) и ``active`` (``True``/``False``). ``sort`` — поля ``UserItem``
        через запятую, ``-`` перед полем — по убыванию. ``contract_id`` оставляет
        пользователей с этим привязанным договором.

        Неизвестные поле сортировки и роль сервер молча игнорирует или отвечает
        пустым списком, поэтому SDK отклоняет их до запроса.
        """
        request = UsersQuery.model_validate(
            {
                "sort": validate_sort_fields(sort, UserItem.model_fields, "пользователя"),
                "page": page,
                "on_page": on_page,
                "q": q,
                "filter": filter,
                "contract_id": contract_id,
            }
        )
        params = request.model_dump(exclude_none=True)
        if request.filter is not None:
            params["filter"] = to_json_param(request.filter.model_dump(exclude_none=True))
        return await self._request(
            GET_USERS,
            api_version=api_version,
            query={key: value for key, value in params.items() if value is not None},
        )

    async def iter_users(
        self,
        *,
        sort: str | None = None,
        q: str | None = None,
        filter: UserFilter | Mapping[str, object] | None = None,
        contract_id: str | None = None,
        on_page: int = 100,
        max_pages: int = 100,
        api_version: str | None = None,
    ) -> AsyncIterator[UserItem]:
        """Последовательно получить пользователей с ограничением числа страниц.

        Фильтры и сортировка — как у ``get_users``.
        """
        validate_positive_count(on_page)
        validate_positive_count(max_pages)
        yielded = 0
        for page in range(1, max_pages + 1):
            response = await self.get_users(
                sort=sort,
                page=page,
                on_page=on_page,
                q=q,
                filter=filter,
                contract_id=contract_id,
                api_version=api_version,
            )
            for item in response.result:
                yield item
                yielded += 1
            if not response.result or yielded >= response.total_count:
                return

    async def create_user(
        self,
        *,
        uuid: str,
        mobile: str,
        api_version: str | None = None,
    ) -> UserCreateResponse:
        """Создать пользователя по внешнему UUID и мобильному номеру.

        Типовой сценарий:
            Создать технического водителя без персональных данных перед
            привязкой карты и договора.

        Пример:
            ``await client.users.create_user(uuid="external-id", mobile="79990000000")``

        ``mobile`` — логин водителя: только цифры, 11–13 знаков, без ``+``. Другой
        формат сервер отклоняет ответом ``400``, поэтому SDK проверяет его до
        платного запроса.
        """
        request = UserCreateRequest(
            uuid=require_identifier(uuid, "uuid"), mobile=validate_mobile(mobile)
        )
        return await self._request(
            CREATE_USER,
            api_version=api_version,
            form=request.model_dump(),
        )

    async def attach_contracts(
        self,
        *,
        user_id: str,
        contracts: list[UserAttachContractRequest | Mapping[str, object]],
        api_version: str | None = None,
    ) -> UserBoolResponse:
        """Привязать договоры и права доступа к пользователю."""
        wire_user_id = require_identifier(user_id, "user_id")
        if not contracts:
            raise RequestValidationError("contracts: необходим хотя бы один элемент")
        payload = [
            UserAttachContractRequest.model_validate(contract).model_dump(exclude_none=True)
            for contract in contracts
        ]
        return await self._request(
            ATTACH_CONTRACTS,
            api_version=api_version,
            path_params={"user_id": wire_user_id},
            json_body=payload,
        )

    async def detach_contracts(
        self,
        *,
        user_id: str,
        contracts: list[str],
        api_version: str | None = None,
    ) -> UserBoolResponse:
        """Отвязать договоры от пользователя."""
        return await self._request(
            DETACH_CONTRACTS,
            api_version=api_version,
            path_params={"user_id": require_identifier(user_id, "user_id")},
            json_body=UserContractsRequest(
                contracts=validate_identifier_list(contracts, "contracts")
            ).contracts,
        )

    async def attach_card(
        self,
        *,
        user_id: str,
        card_id: str,
        api_version: str | None = None,
    ) -> UserBoolResponse:
        """Привязать карту к пользователю."""
        return await self._request(
            ATTACH_CARD,
            api_version=api_version,
            path_params={"user_id": require_identifier(user_id, "user_id")},
            form=UserCardRequest(card_id=require_identifier(card_id, "card_id")).model_dump(),
        )

    async def detach_card(
        self,
        *,
        user_id: str,
        card_id: str,
        api_version: str | None = None,
    ) -> UserBoolResponse:
        """Отвязать карту от пользователя."""
        return await self._request(
            DETACH_CARD,
            api_version=api_version,
            path_params={"user_id": require_identifier(user_id, "user_id")},
            form=UserCardRequest(card_id=require_identifier(card_id, "card_id")).model_dump(),
        )

    async def delete_user(
        self,
        *,
        user_id: str,
        use_post: bool = False,
        api_version: str | None = None,
    ) -> UserBoolResponse:
        """Удалить пользователя через DELETE или POST method override."""
        return await self._request(
            DELETE_USER,
            api_version=api_version,
            route_name="post_override" if use_post else "default",
            path_params={"user_id": require_identifier(user_id, "user_id")},
            form=with_method_override(None, "DELETE") if use_post else None,
        )
