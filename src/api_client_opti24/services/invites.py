from collections.abc import AsyncIterator, Mapping

from ..models.invites import (
    InviteBoolResponse,
    InviteCreateRequest,
    InviteItem,
    InviteListResponse,
    InviteResponse,
)
from ..operations import operation
from ..payloads import with_method_override
from ..service_base import _BaseService
from ..validation import require_identifier, validate_positive_count

GET_INVITES = operation("get_invites", InviteListResponse)
CREATE_INVITE = operation("create_invite", InviteResponse)
DELETE_INVITE = operation("delete_invite", InviteBoolResponse)
RESEND_INVITE = operation("resend_invite", InviteResponse)
PROLONG_INVITE = operation("prolong_invite", InviteBoolResponse)


class InvitesService(_BaseService):
    """Methods for user invitations (v2)."""

    async def get_invites(
        self,
        *,
        role: str | None = None,
        user_id: str | None = None,
        sort: str | None = None,
        status: str | None = None,
        q: str | None = None,
        page: int | None = None,
        on_page: int | None = None,
        api_version: str | None = None,
    ) -> InviteListResponse:
        """Получить страницу приглашений пользователей."""
        if page is not None:
            validate_positive_count(page)
        if on_page is not None:
            validate_positive_count(on_page)
        params = {
            "role": role,
            "user_id": require_identifier(user_id, "user_id") if user_id is not None else None,
            "sort": sort,
            "status": status,
            "q": q,
            "page": page,
            "on_page": on_page,
        }
        return await self._request(
            GET_INVITES,
            api_version=api_version,
            params={key: value for key, value in params.items() if value is not None},
        )

    async def iter_invites(
        self,
        *,
        role: str | None = None,
        status: str | None = None,
        q: str | None = None,
        on_page: int = 100,
        max_pages: int = 100,
        api_version: str | None = None,
    ) -> AsyncIterator[InviteItem]:
        """Последовательно получить приглашения с ограничением числа страниц."""
        validate_positive_count(on_page)
        validate_positive_count(max_pages)
        yielded = 0
        for page in range(1, max_pages + 1):
            response = await self.get_invites(
                role=role,
                status=status,
                q=q,
                page=page,
                on_page=on_page,
                api_version=api_version,
            )
            for item in response.data.result:
                yield item
                yielded += 1
            if not response.data.result or yielded >= response.data.total_count:
                return

    async def create_invite(
        self,
        *,
        data: InviteCreateRequest | Mapping[str, object],
        with_send: bool = True,
        api_version: str | None = None,
    ) -> InviteResponse:
        """Создать приглашение с отправкой или без отправки сообщения.

        Типовой сценарий:
            Пригласить сотрудника и сразу отправить ему сообщение с инструкцией.

        Пример:
            ``await client.invites.create_invite(data=request, with_send=True)``
        """
        payload = InviteCreateRequest.model_validate(data).model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        return await self._request(
            CREATE_INVITE,
            api_version=api_version,
            route_name="default" if with_send else "without_send",
            json=payload,
        )

    async def delete_invite(
        self,
        *,
        invite_id: str,
        use_post: bool = False,
        api_version: str | None = None,
    ) -> InviteBoolResponse:
        """Удалить приглашение через DELETE или POST method override."""
        return await self._request(
            DELETE_INVITE,
            api_version=api_version,
            route_name="post_override" if use_post else "default",
            path_params={"invite_id": require_identifier(invite_id, "invite_id")},
            data=with_method_override(None, "DELETE") if use_post else None,
        )

    async def resend_invite(
        self,
        *,
        invite_id: str,
        api_version: str | None = None,
    ) -> InviteResponse:
        """Повторно отправить приглашение."""
        return await self._request(
            RESEND_INVITE,
            api_version=api_version,
            path_params={"invite_id": require_identifier(invite_id, "invite_id")},
        )

    async def prolong_invite(
        self,
        *,
        invite_id: str,
        with_send: bool = True,
        api_version: str | None = None,
    ) -> InviteBoolResponse:
        """Продлить срок действия приглашения."""
        return await self._request(
            PROLONG_INVITE,
            api_version=api_version,
            route_name="default" if with_send else "without_send",
            path_params={"invite_id": require_identifier(invite_id, "invite_id")},
        )
