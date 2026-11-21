from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, get_args

from ..errors import RequestValidationError
from ..models.request_parts import ContractQuery
from ..models.templates import (
    TemplateCreateRequest,
    TemplateCreateResponse,
    TemplateDeleteResponse,
    TemplateGeoRestrictionCreateRequest,
    TemplateGeoRestrictionCreateResponse,
    TemplateGeoRestrictionDeleteResponse,
    TemplateGeoRestrictionListResponse,
    TemplateLimitCreateRequest,
    TemplateLimitCreateResponse,
    TemplateLimitDeleteResponse,
    TemplateLimitListResponse,
    TemplateRestrictionCreateRequest,
    TemplateRestrictionCreateResponse,
    TemplateRestrictionDeleteResponse,
    TemplateRestrictionListResponse,
    TemplatesListResponse,
)
from ..operations import operation
from ..payloads import with_method_override
from ..service_base import _BaseService
from ..validation import require_identifier, validate_choice

TemplateType = Literal["Limit", "Wallet"]
TEMPLATE_NAME_MAX_LENGTH = 30
TemplatePayloadRequest = (
    TemplateLimitCreateRequest
    | TemplateRestrictionCreateRequest
    | TemplateGeoRestrictionCreateRequest
)

GET_TEMPLATES = operation("get_templates", TemplatesListResponse)
CREATE_TEMPLATE = operation("create_template", TemplateCreateResponse)
UPDATE_TEMPLATE = operation("update_template", TemplateCreateResponse)
DELETE_TEMPLATE = operation("delete_template", TemplateDeleteResponse)
GET_TEMPLATE_LIMITS = operation("get_template_limits", TemplateLimitListResponse)
CREATE_TEMPLATE_LIMIT = operation("create_template_limit", TemplateLimitCreateResponse)
UPDATE_TEMPLATE_LIMIT = operation("update_template_limit", TemplateLimitCreateResponse)
DELETE_TEMPLATE_LIMIT = operation("delete_template_limit", TemplateLimitDeleteResponse)
GET_TEMPLATE_RESTRICTIONS = operation("get_template_restrictions", TemplateRestrictionListResponse)
CREATE_TEMPLATE_RESTRICTION = operation(
    "create_template_restriction", TemplateRestrictionCreateResponse
)
UPDATE_TEMPLATE_RESTRICTION = operation(
    "update_template_restriction", TemplateRestrictionCreateResponse
)
DELETE_TEMPLATE_RESTRICTION = operation(
    "delete_template_restriction", TemplateRestrictionDeleteResponse
)
GET_TEMPLATE_GEORESTRICTIONS = operation(
    "get_template_georestrictions", TemplateGeoRestrictionListResponse
)
CREATE_TEMPLATE_GEORESTRICTION = operation(
    "create_template_georestriction", TemplateGeoRestrictionCreateResponse
)
UPDATE_TEMPLATE_GEORESTRICTION = operation(
    "update_template_georestriction", TemplateGeoRestrictionCreateResponse
)
DELETE_TEMPLATE_GEORESTRICTION = operation(
    "delete_template_georestriction", TemplateGeoRestrictionDeleteResponse
)


def _validate_template_fields(type_: str, name: str) -> str:
    validate_choice(type_, get_args(TemplateType), "type_")
    normalized = require_identifier(name, "name")
    if len(normalized) > TEMPLATE_NAME_MAX_LENGTH:
        raise RequestValidationError(
            f"name: не длиннее {TEMPLATE_NAME_MAX_LENGTH} символов: сервер отклоняет длиннее"
        )
    return normalized


class _TemplateOperationsBase(_BaseService):
    async def _payload_contract_id(
        self,
        payload_contract_id: str | None,
        contract_id: str | None,
    ) -> str:
        if (
            contract_id is not None
            and payload_contract_id is not None
            and require_identifier(contract_id, "contract_id")
            != require_identifier(payload_contract_id, "contract_id")
        ):
            raise RequestValidationError(
                "contract_id в аргументе и в payload различаются: укажите договор один раз"
            )
        if contract_id is not None:
            return await self._resolve_contract_id(contract_id)
        if payload_contract_id is not None:
            return require_identifier(payload_contract_id, "contract_id")
        return await self._resolve_contract_id(None)

    async def _contract_payload(
        self,
        request: TemplatePayloadRequest,
        contract_id: str | None,
    ) -> tuple[str, dict[str, Any]]:
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        payload = request.model_dump(exclude_none=True, by_alias=True)
        payload["contract_id"] = cid
        return cid, payload


class _TemplateCrudOperations(_TemplateOperationsBase):
    """CRUD самого шаблона."""

    async def get_templates(
        self,
        *,
        contract_id: str | None = None,
    ) -> TemplatesListResponse:
        """Получить список шаблонов виртуальных карт выбранного договора.

        Операция ``GET_TEMPLATES``. Договор: явный ``contract_id`` или договор сессии. Аргументы
        проверяются до сети.

        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``TemplatesListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_TEMPLATES,
            query=ContractQuery.create(cid).model_dump(),
            contract_header=cid,
        )

    async def create_template(
        self,
        *,
        type_: TemplateType,
        name: str,
        contract_id: str | None = None,
    ) -> TemplateCreateResponse:
        """Создать шаблон виртуальной карты для выбранного договора (операция ``CREATE_TEMPLATE``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Типовой сценарий:
            Создать лимитный или кошельковый шаблон, который затем можно
            дополнить лимитами и ограничителями.

        Пример вызова:
        ```python
        template = await client.templates.create_template(
            type_="Limit",
            name="Дневной лимит",
        )
        ```

        Пример payload:
        ```json
        {"contract_id": "contract-id", "type": "Limit", "name": "Дневной лимит"}
        ```

        :param type_: Тип карты: ``Limit`` — лимитная схема, ``Wallet`` — электронный кошелёк.
        :param name: Имя шаблона ВК, уникальное в рамках договора.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``TemplateCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_name = _validate_template_fields(type_, name)
        cid = await self._resolve_contract_id(contract_id)
        request = TemplateCreateRequest(contract_id=cid, type=type_, name=wire_name)
        return await self._request(
            CREATE_TEMPLATE,
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )

    async def update_template(
        self,
        *,
        template_id: str,
        type_: TemplateType,
        name: str,
        contract_id: str | None = None,
        use_post: bool = True,
    ) -> TemplateCreateResponse:
        """Изменить существующий шаблон виртуальной карты (операция ``UPDATE_TEMPLATE``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Маршрут принимает только PUT: POST без ``_method=PUT`` сервер отклоняет с
        кодом 405. По умолчанию SDK отправляет POST с ``_method=PUT``;
        ``use_post=False`` отправляет PUT.

        :param template_id: Идентификатор шаблона.
        :param type_: Тип карты: ``Limit`` — лимитная схема, ``Wallet`` — электронный кошелёк.
        :param name: Имя шаблона ВК, уникальное в рамках договора.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param use_post: ``True`` — POST с полем ``_method=PUT`` (для клиентов без PUT);
            ``False`` — прямой PUT.
        :return: ``TemplateCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_template_id = require_identifier(template_id, "template_id")
        wire_name = _validate_template_fields(type_, name)
        cid = await self._resolve_contract_id(contract_id)
        request = TemplateCreateRequest(contract_id=cid, type=type_, name=wire_name)
        form = request.model_dump(exclude_none=True)
        return await self._request(
            UPDATE_TEMPLATE,
            route_name="default" if use_post else "put",
            path_params={"template_id": wire_template_id},
            form=with_method_override(form, "PUT") if use_post else form,
            contract_header=cid,
        )

    async def delete_template(
        self,
        *,
        template_id: str,
        use_post: bool = False,
    ) -> TemplateDeleteResponse:
        """Удалить шаблон виртуальной карты (операция ``DELETE_TEMPLATE``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param use_post: ``True`` — POST с полем ``_method=DELETE`` (для клиентов без DELETE);
            ``False`` — прямой DELETE.
        :return: ``TemplateDeleteResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            DELETE_TEMPLATE,
            route_name="post_override" if use_post else "default",
            path_params={"template_id": require_identifier(template_id, "template_id")},
            form=with_method_override(None, "DELETE") if use_post else None,
        )


class _TemplateLimitOperations(_TemplateOperationsBase):
    """Операции над лимитами шаблона."""

    async def get_template_limits(
        self,
        *,
        template_id: str,
    ) -> TemplateLimitListResponse:
        """Получить список лимитов шаблона виртуальной карты (операция ``GET_TEMPLATE_LIMITS``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :return: ``TemplateLimitListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            GET_TEMPLATE_LIMITS,
            path_params={"template_id": require_identifier(template_id, "template_id")},
        )

    async def create_template_limit(
        self,
        *,
        template_id: str,
        payload: TemplateLimitCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
    ) -> TemplateLimitCreateResponse:
        """Создать лимит шаблона виртуальной карты (операция ``CREATE_TEMPLATE_LIMIT``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param payload: Параметры лимита шаблона ВК: ``contract_id``, ограничение ``amount`` или
            ``sum``, параметры ``time``/``term``, ``product_type``, ``product_group``, а также
            ``create_restriction``.
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :return: ``TemplateLimitCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = TemplateLimitCreateRequest.model_validate(payload)
        wire_template_id = require_identifier(template_id, "template_id")
        cid, request_payload = await self._contract_payload(request, contract_id)
        return await self._request(
            CREATE_TEMPLATE_LIMIT,
            path_params={"template_id": wire_template_id},
            json_body=request_payload,
            contract_header=cid,
        )

    async def update_template_limit(
        self,
        *,
        template_id: str,
        limit_id: str,
        limit: TemplateLimitCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        use_post: bool = True,
    ) -> TemplateLimitCreateResponse:
        """Изменить лимит шаблона (операция ``UPDATE_TEMPLATE_LIMIT``).

        Аргументы проверяются до сети.

        ``limit``: новые параметры лимита ``limit_id``; в теле запроса SDK
        отправляет объект лимита. Массив сервер не принимает: из него он не читает
        ``_method`` и отвечает кодом 405.

        :param template_id: Идентификатор шаблона.
        :param limit_id: ID лимита шаблона ВК.
        :param limit: Параметры изменения лимита: ограничение ``amount`` или ``sum``,
            ``time``/``term``, ``product_type``, ``product_group``; ``contract_id`` изменить
            нельзя.
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :param use_post: ``True`` — POST с полем ``_method=PUT`` (для клиентов без PUT);
            ``False`` — прямой PUT.
        :return: ``TemplateLimitCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = TemplateLimitCreateRequest.model_validate(limit)
        path_params = {
            "template_id": require_identifier(template_id, "template_id"),
            "limit_id": require_identifier(limit_id, "limit_id"),
        }
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        request_limit = request.model_dump(exclude_none=True, by_alias=True)
        request_limit["contract_id"] = cid
        if use_post:
            request_limit = with_method_override(request_limit, "PUT")
        return await self._request(
            UPDATE_TEMPLATE_LIMIT,
            route_name="default" if use_post else "put",
            path_params=path_params,
            json_body=request_limit,
            contract_header=cid,
        )

    async def delete_template_limit(
        self,
        *,
        template_id: str,
        limit_id: str,
        use_post: bool = False,
    ) -> TemplateLimitDeleteResponse:
        """Удалить лимит шаблона виртуальной карты (операция ``DELETE_TEMPLATE_LIMIT``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param limit_id: ID лимита шаблона ВК.
        :param use_post: ``True`` — POST с полем ``_method=DELETE`` (для клиентов без DELETE);
            ``False`` — прямой DELETE.
        :return: ``TemplateLimitDeleteResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            DELETE_TEMPLATE_LIMIT,
            route_name="post_override" if use_post else "default",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "limit_id": require_identifier(limit_id, "limit_id"),
            },
            form=with_method_override(None, "DELETE") if use_post else None,
        )


class _TemplateRestrictionOperations(_TemplateOperationsBase):
    """Операции над товарными ограничителями шаблона."""

    async def get_template_restrictions(
        self,
        *,
        template_id: str,
    ) -> TemplateRestrictionListResponse:
        """Получить список ограничителей шаблона (операция ``GET_TEMPLATE_RESTRICTIONS``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :return: ``TemplateRestrictionListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            GET_TEMPLATE_RESTRICTIONS,
            path_params={"template_id": require_identifier(template_id, "template_id")},
        )

    async def create_template_restriction(
        self,
        *,
        template_id: str,
        payload: TemplateRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
    ) -> TemplateRestrictionCreateResponse:
        """Создать ограничитель шаблона (операция ``CREATE_TEMPLATE_RESTRICTION``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param payload: Параметры ограничителя: ``contract_id``, ``product_type``,
            ``product_group``, ``restriction_type`` (``1`` — разрешающий, ``2`` — запрещающий).
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :return: ``TemplateRestrictionCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = TemplateRestrictionCreateRequest.model_validate(payload)
        wire_template_id = require_identifier(template_id, "template_id")
        cid, request_payload = await self._contract_payload(request, contract_id)
        return await self._request(
            CREATE_TEMPLATE_RESTRICTION,
            path_params={"template_id": wire_template_id},
            json_body=request_payload,
            contract_header=cid,
        )

    async def update_template_restriction(
        self,
        *,
        template_id: str,
        restriction_id: str,
        payload: TemplateRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        use_post: bool = True,
    ) -> TemplateRestrictionCreateResponse:
        """Изменить ограничитель шаблона (операция ``UPDATE_TEMPLATE_RESTRICTION``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param restriction_id: ID ограничителя шаблона ВК.
        :param payload: Изменяемые параметры ограничителя: ``product_type``, ``product_group``,
            ``restriction_type``; ``contract_id`` изменить нельзя.
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :param use_post: ``True`` — POST с полем ``_method=PUT`` (для клиентов без PUT);
            ``False`` — прямой PUT.
        :return: ``TemplateRestrictionCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = TemplateRestrictionCreateRequest.model_validate(payload)
        path_params = {
            "template_id": require_identifier(template_id, "template_id"),
            "restriction_id": require_identifier(restriction_id, "restriction_id"),
        }
        cid, request_payload = await self._contract_payload(request, contract_id)
        if use_post:
            request_payload = with_method_override(request_payload, "PUT")
        return await self._request(
            UPDATE_TEMPLATE_RESTRICTION,
            route_name="default" if use_post else "put",
            path_params=path_params,
            json_body=request_payload,
            contract_header=cid,
        )

    async def delete_template_restriction(
        self,
        *,
        template_id: str,
        restriction_id: str,
        use_post: bool = False,
    ) -> TemplateRestrictionDeleteResponse:
        """Удалить ограничитель шаблона (операция ``DELETE_TEMPLATE_RESTRICTION``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param restriction_id: ID ограничителя шаблона ВК.
        :param use_post: ``True`` — POST с полем ``_method=DELETE`` (для клиентов без DELETE);
            ``False`` — прямой DELETE.
        :return: ``TemplateRestrictionDeleteResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            DELETE_TEMPLATE_RESTRICTION,
            route_name="post_override" if use_post else "default",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "restriction_id": require_identifier(restriction_id, "restriction_id"),
            },
            form=with_method_override(None, "DELETE") if use_post else None,
        )


class _TemplateGeoRestrictionOperations(_TemplateOperationsBase):
    """Операции над географическими ограничителями шаблона."""

    async def get_template_georestrictions(
        self,
        *,
        template_id: str,
    ) -> TemplateGeoRestrictionListResponse:
        """Получить список геоограничителей шаблона (операция ``GET_TEMPLATE_GEORESTRICTIONS``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :return: ``TemplateGeoRestrictionListResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            GET_TEMPLATE_GEORESTRICTIONS,
            path_params={"template_id": require_identifier(template_id, "template_id")},
        )

    async def create_template_georestriction(
        self,
        *,
        template_id: str,
        payload: TemplateGeoRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
    ) -> TemplateGeoRestrictionCreateResponse:
        """Создать геоограничитель шаблона (операция ``CREATE_TEMPLATE_GEORESTRICTION``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param payload: Параметры геоограничителя: ``contract_id``, ``country``, ``region``,
            ``partner``, ``service_center``, ``restriction_type`` (``1`` — разрешающий, ``2`` —
            запрещающий).
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :return: ``TemplateGeoRestrictionCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = TemplateGeoRestrictionCreateRequest.model_validate(payload)
        wire_template_id = require_identifier(template_id, "template_id")
        cid, request_payload = await self._contract_payload(request, contract_id)
        return await self._request(
            CREATE_TEMPLATE_GEORESTRICTION,
            path_params={"template_id": wire_template_id},
            json_body=request_payload,
            contract_header=cid,
        )

    async def update_template_georestriction(
        self,
        *,
        template_id: str,
        georestriction_id: str,
        payload: TemplateGeoRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        use_post: bool = True,
    ) -> TemplateGeoRestrictionCreateResponse:
        """Изменить геоограничитель шаблона (операция ``UPDATE_TEMPLATE_GEORESTRICTION``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param georestriction_id: ID геоограничителя шаблона ВК.
        :param payload: Изменяемые параметры геоограничителя: ``country``, ``region``,
            ``partner``, ``service_center``, ``restriction_type``; ``contract_id`` изменить
            нельзя.
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :param use_post: ``True`` — POST с полем ``_method=PUT`` (для клиентов без PUT);
            ``False`` — прямой PUT.
        :return: ``TemplateGeoRestrictionCreateResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        request = TemplateGeoRestrictionCreateRequest.model_validate(payload)
        path_params = {
            "template_id": require_identifier(template_id, "template_id"),
            "georestriction_id": require_identifier(georestriction_id, "georestriction_id"),
        }
        cid, request_payload = await self._contract_payload(request, contract_id)
        if use_post:
            request_payload = with_method_override(request_payload, "PUT")
        return await self._request(
            UPDATE_TEMPLATE_GEORESTRICTION,
            route_name="default" if use_post else "put",
            path_params=path_params,
            json_body=request_payload,
            contract_header=cid,
        )

    async def delete_template_georestriction(
        self,
        *,
        template_id: str,
        georestriction_id: str,
        use_post: bool = False,
    ) -> TemplateGeoRestrictionDeleteResponse:
        """Удалить геоограничитель шаблона (операция ``DELETE_TEMPLATE_GEORESTRICTION``).

        Аргументы проверяются до сети.

        :param template_id: Идентификатор шаблона.
        :param georestriction_id: ID геоограничителя шаблона ВК.
        :param use_post: ``True`` — POST с полем ``_method=DELETE`` (для клиентов без DELETE);
            ``False`` — прямой DELETE.
        :return: ``TemplateGeoRestrictionDeleteResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        return await self._request(
            DELETE_TEMPLATE_GEORESTRICTION,
            route_name="post_override" if use_post else "default",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "georestriction_id": require_identifier(
                    georestriction_id,
                    "georestriction_id",
                ),
            },
            form=with_method_override(None, "DELETE") if use_post else None,
        )


class TemplatesService(
    _TemplateCrudOperations,
    _TemplateLimitOperations,
    _TemplateRestrictionOperations,
    _TemplateGeoRestrictionOperations,
):
    """Фасад управления шаблонами, собранный из узких групп операций."""
