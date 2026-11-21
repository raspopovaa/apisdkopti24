from collections.abc import AsyncIterator, Mapping
from typing import Literal, get_args

from ..errors import RequestValidationError
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
from ..utils import to_json_param
from ..validation import (
    require_identifier,
    validate_choice,
    validate_positive_count,
    validate_sort_fields,
)
from ._shared import paginate

GET_INVITES = operation("get_invites", InviteListResponse)
CREATE_INVITE = operation("create_invite", InviteResponse)
DELETE_INVITE = operation("delete_invite", InviteBoolResponse)
RESEND_INVITE = operation("resend_invite", InviteResponse)
PROLONG_INVITE = operation("prolong_invite", InviteBoolResponse)

InviteRoleFilter = Literal["Supervisor", "Regulatory", "Driver", "Readonly"]
InviteStatus = Literal["Active", "Expired", "Finished"]


class InvitesService(_BaseService):
    """Методы работы с приглашениями пользователей (v2)."""

    async def get_invites(
        self,
        *,
        role: InviteRoleFilter | None = None,
        user_id: bool | None = None,
        sort: str | None = None,
        status: InviteStatus | None = None,
        q: str | None = None,
        filter: Mapping[str, object] | None = None,
        page: int | None = None,
        on_page: int | None = None,
    ) -> InviteListResponse:
        """Получить страницу приглашений пользователей (операция ``GET_INVITES``).

        Аргументы проверяются до сети.

        ``role``: ``Supervisor``, ``Regulatory``, ``Driver`` или ``Readonly``;
        ``status``: ``Active``, ``Expired`` или ``Finished``. ``user_id=True`` по
        спецификации показывает приглашения, по которым зарегистрировался
        пользователь; SDK отправляет ``true``/``false``. ``sort``: поля
        ``InviteItem`` через запятую, ``-`` перед полем: по убыванию. Неверные
        значения SDK отклоняет до запроса (``RequestValidationError``).

        :param role: Фильтр по ID роли: ``Supervisor``, ``Regulatory``, ``Driver`` или
            ``Readonly``.
        :param user_id: Флаг, а не ID: True показывает приглашения, по которым зарегистрировался
            пользователь. SDK отправляет true или false.
        :param sort: Поля приглашения через запятую, «-» перед полем — по убыванию. Неизвестное
            поле SDK отклоняет до запроса: сервер ответил бы 500.
        :param status: Статус ответа API
        :param q: Строка полнотекстового поиска.
        :param filter: Объект фильтрации, SDK передаёт его JSON-строкой, например ``{"status":
            "Finished", "role": "Driver"}``.
        :param page: Номер страницы результата.
        :param on_page: Количество элементов на странице.
        :return: ``InviteListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        if page is not None:
            validate_positive_count(page)
        if on_page is not None:
            validate_positive_count(on_page)
        validate_choice(role, get_args(InviteRoleFilter), "role")
        validate_choice(status, get_args(InviteStatus), "status")
        if user_id is not None and not isinstance(user_id, bool):
            raise RequestValidationError("user_id: флаг True или False, а не ID пользователя")
        # На неизвестное поле сортировки сервер отвечает 500, а не 400.
        params = {
            "role": role,
            "user_id": ("true" if user_id else "false") if user_id is not None else None,
            "sort": validate_sort_fields(sort, InviteItem.model_fields, "приглашения"),
            "status": status,
            "q": q,
            "filter": to_json_param(dict(filter)) if filter is not None else None,
            "page": page,
            "on_page": on_page,
        }
        return await self._request(
            GET_INVITES,
            query={key: value for key, value in params.items() if value is not None},
        )

    async def iter_invites(
        self,
        *,
        role: InviteRoleFilter | None = None,
        user_id: bool | None = None,
        sort: str | None = None,
        status: InviteStatus | None = None,
        q: str | None = None,
        filter: Mapping[str, object] | None = None,
        on_page: int = 100,
        max_pages: int = 100,
        strict: bool = False,
    ) -> AsyncIterator[InviteItem]:
        """Последовательно получить приглашения с ограничением числа страниц.

        Аргументы проверяются до первого запроса.

        Фильтры и сортировка: как у ``get_invites``.

        Если ``max_pages`` закончились раньше ``total_count``, перебор останавливается
        с предупреждением в журнале, а при ``strict=True``: с ``PaginationLimitError``.

        :param on_page: Приглашений на странице, больше 0.
        :param max_pages: Наибольшее число страниц (запросов), больше 0.
        :param strict: Что делать, если ``max_pages`` кончились раньше ``total_count``:
            ``False`` — остановиться и записать предупреждение в журнал, ``True`` — поднять
            ``PaginationLimitError``.
        :return: Асинхронный итератор ``InviteItem``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запросы не отправлены.
        :raises PaginationLimitError: Только при ``strict=True``: приглашений больше, чем
            помещается в ``max_pages`` страниц.
        :raises Opti24Error: Ошибка API или сети на любой странице; уже выданные элементы
            остаются у вызывающего кода.
        """
        validate_positive_count(on_page)
        validate_positive_count(max_pages)

        async def fetch_page(page_index: int) -> tuple[list[InviteItem], int]:
            response = await self.get_invites(
                role=role,
                user_id=user_id,
                sort=sort,
                status=status,
                q=q,
                filter=filter,
                page=page_index + 1,
                on_page=on_page,
            )
            return list(response.data.result or []), response.data.total_count

        async for item in paginate(
            fetch_page,
            max_pages=max_pages,
            operation="iter_invites",
            logger=self.logger,
            strict=strict,
        ):
            yield item

    async def create_invite(
        self,
        *,
        data: InviteCreateRequest | Mapping[str, object],
        with_send: bool = True,
    ) -> InviteResponse:
        """Создать приглашение с отправкой или без отправки сообщения (операция ``CREATE_INVITE``).

        Аргументы проверяются до сети.

        Типовой сценарий:
            Пригласить сотрудника и сразу отправить ему сообщение с инструкцией.

        Пример:
            ``await client.invites.create_invite(data=request, with_send=True)``

        :param data: Типизированные данные ответа API
        :param with_send: ``True`` — сервер сам отправит приглашение (SMS или email); ``False``
            — только создаст его, ссылку из ответа передайте сами.
        :return: ``InviteResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        # exclude_unset: в JSON уходят только поля, переданные вызывающим кодом, а не
        # умолчания модели.
        payload = InviteCreateRequest.model_validate(data).model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        # without_send — отдельный маршрут invites_free: приглашение создаётся без
        # SMS и email, ссылку из ответа передают сами.
        return await self._request(
            CREATE_INVITE,
            route_name="default" if with_send else "without_send",
            json_body=payload,
        )

    async def delete_invite(
        self,
        *,
        invite_id: str,
        use_post: bool = False,
    ) -> InviteBoolResponse:
        """Удалить приглашение (операция ``DELETE_INVITE``).

        Аргументы проверяются до сети.

        :param invite_id: Идентификатор приглашения.
        :param use_post: ``True`` — POST с полем ``_method=DELETE`` (для клиентов без DELETE);
            ``False`` — прямой DELETE.
        :return: ``InviteBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        # Спецификация разрешает клиентам без DELETE отправлять POST с _method=DELETE;
        # в каталоге это отдельный маршрут post_override.
        return await self._request(
            DELETE_INVITE,
            route_name="post_override" if use_post else "default",
            path_params={"invite_id": require_identifier(invite_id, "invite_id")},
            form=with_method_override(None, "DELETE") if use_post else None,
        )

    async def resend_invite(
        self,
        *,
        invite_id: str,
    ) -> InviteResponse:
        """Повторно отправить приглашение (операция ``RESEND_INVITE``).

        Аргументы проверяются до сети.

        :param invite_id: Идентификатор приглашения.
        :return: ``InviteResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            RESEND_INVITE,
            path_params={"invite_id": require_identifier(invite_id, "invite_id")},
        )

    async def prolong_invite(
        self,
        *,
        invite_id: str,
        with_send: bool = True,
    ) -> InviteBoolResponse:
        """Продлить срок действия приглашения (операция ``PROLONG_INVITE``).

        Аргументы проверяются до сети.

        :param invite_id: Идентификатор приглашения.
        :param with_send: ``True`` — после продления сервер повторно отправит приглашение;
            ``False`` — только продлит срок.
        :return: ``InviteBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            PROLONG_INVITE,
            route_name="default" if with_send else "without_send",
            path_params={"invite_id": require_identifier(invite_id, "invite_id")},
        )
