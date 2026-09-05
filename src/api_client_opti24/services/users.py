from collections.abc import AsyncIterator, Mapping
from typing import Any

from ..models.users import (
    UserAttachContractRequest,
    UserBoolResponse,
    UserCreateResponse,
    UserItem,
    UserListResponse,
)
from ..operations import operation
from ..payloads import with_method_override
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import (
    require_identifier,
    validate_identifier_list,
    validate_non_empty_value,
    validate_positive_count,
)

GET_USERS = operation("get_users", UserListResponse)
CREATE_USER = operation("create_user", UserCreateResponse)
ATTACH_CONTRACTS = operation("attach_contracts", UserBoolResponse)
DETACH_CONTRACTS = operation("detach_contracts", UserBoolResponse)
ATTACH_CARD = operation("attach_card", UserBoolResponse)
DETACH_CARD = operation("detach_card", UserBoolResponse)
DELETE_USER = operation("delete_user", UserBoolResponse)


class UsersService(_BaseService):
    """Methods for users (v2)."""

    async def get_users(
        self,
        *,
        sort: str | None = None,
        page: int | None = None,
        on_page: int | None = None,
        q: str | None = None,
        filter: dict[str, Any] | None = None,
        api_version: str | None = None,
    ) -> UserListResponse:
        """Получить страницу пользователей корпоративного клиента."""
        if page is not None:
            validate_positive_count(page)
        if on_page is not None:
            validate_positive_count(on_page)
        params = {
            "sort": validate_non_empty_value(sort, "sort") if sort is not None else None,
            "page": page,
            "on_page": on_page,
            "q": q,
            "filter": to_json_param(filter) if filter else None,
        }
        return await self._request(
            GET_USERS,
            api_version=api_version,
            params={key: value for key, value in params.items() if value is not None},
        )

    async def iter_users(
        self,
        *,
        sort: str | None = None,
        q: str | None = None,
        filter: dict[str, Any] | None = None,
        on_page: int = 100,
        max_pages: int = 100,
        api_version: str | None = None,
    ) -> AsyncIterator[UserItem]:
        """Последовательно получить пользователей с ограничением числа страниц."""
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
        """
        return await self._request(
            CREATE_USER,
            api_version=api_version,
            data={
                "uuid": validate_non_empty_value(uuid, "uuid"),
                "mobile": validate_non_empty_value(mobile, "mobile"),
            },
        )

    async def attach_contracts(
        self,
        *,
        user_id: str,
        contracts: list[UserAttachContractRequest | Mapping[str, object]],
        api_version: str | None = None,
    ) -> UserBoolResponse:
        """Привязать договоры и права доступа к пользователю."""
        if not contracts:
            raise ValueError("contracts must contain at least one item")
        payload = [
            UserAttachContractRequest.model_validate(contract).model_dump(exclude_none=True)
            for contract in contracts
        ]
        return await self._request(
            ATTACH_CONTRACTS,
            api_version=api_version,
            path_params={"user_id": require_identifier(user_id, "user_id")},
            json=payload,
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
            json=validate_identifier_list(contracts, "contracts"),
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
            data={"card_id": require_identifier(card_id, "card_id")},
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
            data={"card_id": require_identifier(card_id, "card_id")},
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
            data=with_method_override(None, "DELETE") if use_post else None,
        )
