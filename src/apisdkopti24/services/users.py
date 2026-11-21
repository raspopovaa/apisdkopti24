from collections.abc import AsyncIterator, Mapping, Sequence

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
from ._shared import paginate

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
    ) -> UserListResponse:
        """Получить страницу пользователей корпоративного клиента (операция ``GET_USERS``).

        Аргументы проверяются до сети.

        ``q`` ищет по фамилии, имени, отчеству, логину, email и мобильному телефону.
        ``filter``: ``role`` (``Supervisor``, ``Regulatory``, ``Driver`` или
        ``Readonly``) и ``active`` (``True``/``False``). ``sort``: поля ``UserItem``
        через запятую, ``-`` перед полем: по убыванию. ``contract_id`` оставляет
        пользователей с этим привязанным договором.

        Неизвестные поле сортировки и роль сервер молча игнорирует или отвечает
        пустым списком, поэтому SDK отклоняет их до запроса.

        :param sort: Поля пользователя через запятую, «-» перед полем — по убыванию. Неизвестное
            поле SDK отклоняет до запроса: сервер молча проигнорировал бы его.
        :param page: Номер страницы результата.
        :param on_page: Количество элементов на странице.
        :param q: Строка полнотекстового поиска.
        :param filter: Объект фильтрации пользователей, например ``{"role": "Driver", "active":
            true}``.
        :param contract_id: Оставить пользователей с этим привязанным договором.
        :return: ``UserListResponse``: ``response.result`` (элементы) и ``response.total_count``
            (всего по запросу).
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
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
        strict: bool = False,
    ) -> AsyncIterator[UserItem]:
        """Последовательно получить пользователей с ограничением числа страниц.

        Аргументы проверяются до первого запроса.

        Фильтры и сортировка, включая ``contract_id``: как у ``get_users``.

        Если ``max_pages`` закончились раньше ``total_count``, перебор останавливается
        с предупреждением в журнале, а при ``strict=True``: с ``PaginationLimitError``.

        :param on_page: Пользователей на странице, больше 0.
        :param max_pages: Наибольшее число страниц (запросов), больше 0.
        :param strict: Что делать, если ``max_pages`` кончились раньше ``total_count``:
            ``False`` — остановиться и записать предупреждение в журнал, ``True`` — поднять
            ``PaginationLimitError``.
        :return: Асинхронный итератор ``UserItem``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запросы не отправлены.
        :raises PaginationLimitError: Только при ``strict=True``: пользователей больше, чем
            помещается в ``max_pages`` страниц.
        :raises Opti24Error: Ошибка API или сети на любой странице; уже выданные элементы
            остаются у вызывающего кода.
        """
        validate_positive_count(on_page)
        validate_positive_count(max_pages)

        async def fetch_page(page_index: int) -> tuple[list[UserItem], int]:
            response = await self.get_users(
                sort=sort,
                page=page_index + 1,
                on_page=on_page,
                q=q,
                filter=filter,
                contract_id=contract_id,
            )
            return list(response.result), response.total_count

        async for item in paginate(
            fetch_page,
            max_pages=max_pages,
            operation="iter_users",
            logger=self.logger,
            strict=strict,
        ):
            yield item

    async def create_user(
        self,
        *,
        uuid: str,
        mobile: str,
    ) -> UserCreateResponse:
        """Создать пользователя по внешнему UUID и мобильному номеру (операция ``CREATE_USER``).

        Аргументы проверяются до сети.

        Типовой сценарий:
            Создать технического водителя без персональных данных перед
            привязкой карты и договора.

        Пример:
            ``await client.users.create_user(uuid="external-id", mobile="79990000000")``

        ``mobile`` (логин водителя) содержит только цифры, 11–13 знаков, без ``+``. Другой
        формат сервер отклоняет ответом ``400``, поэтому SDK проверяет его до
        платного запроса.

        :param uuid: Внутренний ID водителя в системе клиента.
        :param mobile: Телефон водителя, используемый как логин.
        :return: ``UserCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = UserCreateRequest(
            uuid=require_identifier(uuid, "uuid"), mobile=validate_mobile(mobile)
        )
        return await self._request(
            CREATE_USER,
            form=request.model_dump(),
        )

    async def attach_contracts(
        self,
        *,
        user_id: str,
        contracts: Sequence[UserAttachContractRequest | Mapping[str, object]],
    ) -> UserBoolResponse:
        """Привязать договоры и права доступа к пользователю (операция ``ATTACH_CONTRACTS``).

        Аргументы проверяются до сети.

        :param user_id: Идентификатор пользователя.
        :param contracts: Список договоров для прикрепления к пользователю. Для каждого договора
            указываются ``sid`` — ID договора, ``template_id`` — ID шаблона ВК, ``use_mpc`` —
            разрешение выпуска МПК (``true``/``false``).
        :return: ``UserBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_user_id = require_identifier(user_id, "user_id")
        if not contracts:
            raise RequestValidationError("contracts: необходим хотя бы один элемент")
        payload = [
            UserAttachContractRequest.model_validate(contract).model_dump(exclude_none=True)
            for contract in contracts
        ]
        return await self._request(
            ATTACH_CONTRACTS,
            path_params={"user_id": wire_user_id},
            json_body=payload,
        )

    async def detach_contracts(
        self,
        *,
        user_id: str,
        contracts: list[str],
    ) -> UserBoolResponse:
        """Отвязать договоры от пользователя (операция ``DETACH_CONTRACTS``).

        Аргументы проверяются до сети.

        :param user_id: Идентификатор пользователя.
        :param contracts: Список ID договоров, которые нужно открепить от пользователя.
        :return: ``UserBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            DETACH_CONTRACTS,
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
    ) -> UserBoolResponse:
        """Привязать карту к пользователю (операция ``ATTACH_CARD``).

        Аргументы проверяются до сети.

        :param user_id: Идентификатор пользователя.
        :param card_id: Идентификатор топливной карты.
        :return: ``UserBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            ATTACH_CARD,
            path_params={"user_id": require_identifier(user_id, "user_id")},
            form=UserCardRequest(card_id=require_identifier(card_id, "card_id")).model_dump(),
        )

    async def detach_card(
        self,
        *,
        user_id: str,
        card_id: str,
    ) -> UserBoolResponse:
        """Отвязать карту от пользователя (операция ``DETACH_CARD``).

        Аргументы проверяются до сети.

        :param user_id: Идентификатор пользователя.
        :param card_id: Идентификатор топливной карты.
        :return: ``UserBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            DETACH_CARD,
            path_params={"user_id": require_identifier(user_id, "user_id")},
            form=UserCardRequest(card_id=require_identifier(card_id, "card_id")).model_dump(),
        )

    async def delete_user(
        self,
        *,
        user_id: str,
        use_post: bool = False,
    ) -> UserBoolResponse:
        """Удалить пользователя (операция ``DELETE_USER``).

        Аргументы проверяются до сети.

        :param user_id: Идентификатор пользователя.
        :param use_post: ``True`` — POST с полем ``_method=DELETE`` (для клиентов без DELETE);
            ``False`` — прямой DELETE.
        :return: ``UserBoolResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        # Спецификация разрешает клиентам без DELETE отправлять POST с _method=DELETE;
        # в каталоге это отдельный маршрут post_override.
        return await self._request(
            DELETE_USER,
            route_name="post_override" if use_post else "default",
            path_params={"user_id": require_identifier(user_id, "user_id")},
            form=with_method_override(None, "DELETE") if use_post else None,
        )
