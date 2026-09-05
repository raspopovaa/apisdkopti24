from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

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
from ..validation import require_identifier

TemplateType = Literal["Limit", "Wallet"]

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


class TemplatesService(_BaseService):
    """Управление шаблонами виртуальных карт и их ограничениями."""

    async def _payload_contract_id(
        self,
        payload_contract_id: str | None,
        contract_id: str | None,
    ) -> str:
        if contract_id is not None:
            return await self._resolve_contract_id(contract_id)
        if payload_contract_id is not None:
            return require_identifier(payload_contract_id, "contract_id")
        return await self._resolve_contract_id(None)

    async def get_templates(
        self,
        *,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TemplatesListResponse:
        """Получить список шаблонов виртуальных карт выбранного договора."""
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            GET_TEMPLATES,
            api_version=api_version,
            params={"contract_id": cid},
            request_contract_id=cid,
        )

    async def create_template(
        self,
        *,
        type_: TemplateType,
        name: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TemplateCreateResponse:
        """Создать шаблон виртуальной карты для выбранного договора.

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
        """
        cid = await self._resolve_contract_id(contract_id)
        request = TemplateCreateRequest(
            contract_id=cid,
            type=type_,
            name=require_identifier(name, "name"),
        )
        return await self._request(
            CREATE_TEMPLATE,
            api_version=api_version,
            data=request.model_dump(exclude_none=True),
            request_contract_id=cid,
        )

    async def update_template(
        self,
        *,
        template_id: str,
        type_: TemplateType,
        name: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TemplateCreateResponse:
        """Изменить существующий шаблон виртуальной карты."""
        cid = await self._resolve_contract_id(contract_id)
        request = TemplateCreateRequest(
            contract_id=cid,
            type=type_,
            name=require_identifier(name, "name"),
        )
        return await self._request(
            UPDATE_TEMPLATE,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
            data=request.model_dump(exclude_none=True),
            request_contract_id=cid,
        )

    async def delete_template(
        self,
        *,
        template_id: str,
        api_version: str | None = None,
        use_post: bool = False,
    ) -> TemplateDeleteResponse:
        """Удалить шаблон виртуальной карты."""
        return await self._request(
            DELETE_TEMPLATE,
            api_version=api_version,
            route_name="post_override" if use_post else "default",
            path_params={"template_id": require_identifier(template_id, "template_id")},
            data=with_method_override(None, "DELETE") if use_post else None,
        )

    async def get_template_limits(
        self,
        *,
        template_id: str,
        api_version: str | None = None,
    ) -> TemplateLimitListResponse:
        """Получить список лимитов шаблона виртуальной карты."""
        return await self._request(
            GET_TEMPLATE_LIMITS,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
        )

    async def create_template_limit(
        self,
        *,
        template_id: str,
        payload: TemplateLimitCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TemplateLimitCreateResponse:
        """Создать лимит шаблона виртуальной карты."""
        request = TemplateLimitCreateRequest.model_validate(payload)
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        request_payload = request.model_dump(exclude_none=True, by_alias=True)
        request_payload["contract_id"] = cid
        return await self._request(
            CREATE_TEMPLATE_LIMIT,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
            json=request_payload,
            request_contract_id=cid,
        )

    async def update_template_limit(
        self,
        *,
        template_id: str,
        limit_id: str,
        limits: list[TemplateLimitCreateRequest | Mapping[str, Any]],
        contract_id: str | None = None,
        use_post: bool = True,
        api_version: str | None = None,
    ) -> TemplateLimitCreateResponse:
        """Изменить лимит шаблона через PUT или POST method override."""
        if not limits:
            raise ValueError("limits must contain at least one item")
        request_limits: list[dict[str, Any]] = []
        for item in limits:
            request = TemplateLimitCreateRequest.model_validate(item)
            if request.amount is None and request.sum is None:
                raise ValueError("each template limit must contain amount or sum")
            cid = await self._payload_contract_id(request.contract_id, contract_id)
            serialized = request.model_dump(exclude_none=True, by_alias=True)
            serialized["contract_id"] = cid
            request_limits.append(serialized)
        if use_post:
            request_limits = with_method_override(request_limits, "PUT")
        self.logger.info(
            "Updating template limit item_count=%d post_fallback=%s",
            len(request_limits),
            use_post,
        )
        return await self._request(
            UPDATE_TEMPLATE_LIMIT,
            api_version=api_version,
            route_name="default" if use_post else "put",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "limit_id": require_identifier(limit_id, "limit_id"),
            },
            json=request_limits,
            request_contract_id=request_limits[0]["contract_id"],
        )

    async def delete_template_limit(
        self,
        *,
        template_id: str,
        limit_id: str,
        api_version: str | None = None,
        use_post: bool = False,
    ) -> TemplateLimitDeleteResponse:
        """Удалить лимит шаблона виртуальной карты."""
        return await self._request(
            DELETE_TEMPLATE_LIMIT,
            api_version=api_version,
            route_name="post_override" if use_post else "default",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "limit_id": require_identifier(limit_id, "limit_id"),
            },
            data=with_method_override(None, "DELETE") if use_post else None,
        )

    async def get_template_restrictions(
        self,
        *,
        template_id: str,
        api_version: str | None = None,
    ) -> TemplateRestrictionListResponse:
        """Получить список ограничителей шаблона."""
        return await self._request(
            GET_TEMPLATE_RESTRICTIONS,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
        )

    async def create_template_restriction(
        self,
        *,
        template_id: str,
        payload: TemplateRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TemplateRestrictionCreateResponse:
        """Создать ограничитель шаблона."""
        request = TemplateRestrictionCreateRequest.model_validate(payload)
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        request_payload = request.model_dump(exclude_none=True, by_alias=True)
        request_payload["contract_id"] = cid
        return await self._request(
            CREATE_TEMPLATE_RESTRICTION,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
            json=request_payload,
            request_contract_id=cid,
        )

    async def update_template_restriction(
        self,
        *,
        template_id: str,
        restriction_id: str,
        payload: TemplateRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        api_version: str | None = None,
        use_post: bool = True,
    ) -> TemplateRestrictionCreateResponse:
        """Изменить ограничитель шаблона через PUT или POST override."""
        request = TemplateRestrictionCreateRequest.model_validate(payload)
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        request_payload = request.model_dump(exclude_none=True, by_alias=True)
        request_payload["contract_id"] = cid
        if use_post:
            request_payload = with_method_override(request_payload, "PUT")
        self.logger.info("Updating template restriction post_fallback=%s", use_post)
        return await self._request(
            UPDATE_TEMPLATE_RESTRICTION,
            api_version=api_version,
            route_name="default" if use_post else "put",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "restriction_id": require_identifier(restriction_id, "restriction_id"),
            },
            json=request_payload,
            request_contract_id=cid,
        )

    async def delete_template_restriction(
        self,
        *,
        template_id: str,
        restriction_id: str,
        api_version: str | None = None,
        use_post: bool = False,
    ) -> TemplateRestrictionDeleteResponse:
        """Удалить ограничитель шаблона."""
        return await self._request(
            DELETE_TEMPLATE_RESTRICTION,
            api_version=api_version,
            route_name="post_override" if use_post else "default",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "restriction_id": require_identifier(restriction_id, "restriction_id"),
            },
            data=with_method_override(None, "DELETE") if use_post else None,
        )

    async def get_template_georestrictions(
        self,
        *,
        template_id: str,
        api_version: str | None = None,
    ) -> TemplateGeoRestrictionListResponse:
        """Получить список геоограничителей шаблона."""
        return await self._request(
            GET_TEMPLATE_GEORESTRICTIONS,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
        )

    async def create_template_georestriction(
        self,
        *,
        template_id: str,
        payload: TemplateGeoRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> TemplateGeoRestrictionCreateResponse:
        """Создать геоограничитель шаблона."""
        request = TemplateGeoRestrictionCreateRequest.model_validate(payload)
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        request_payload = request.model_dump(exclude_none=True, by_alias=True)
        request_payload["contract_id"] = cid
        return await self._request(
            CREATE_TEMPLATE_GEORESTRICTION,
            api_version=api_version,
            path_params={"template_id": require_identifier(template_id, "template_id")},
            json=request_payload,
            request_contract_id=cid,
        )

    async def update_template_georestriction(
        self,
        *,
        template_id: str,
        georestriction_id: str,
        payload: TemplateGeoRestrictionCreateRequest | Mapping[str, Any],
        contract_id: str | None = None,
        api_version: str | None = None,
        use_post: bool = True,
    ) -> TemplateGeoRestrictionCreateResponse:
        """Изменить геоограничитель шаблона через PUT или POST override."""
        request = TemplateGeoRestrictionCreateRequest.model_validate(payload)
        cid = await self._payload_contract_id(request.contract_id, contract_id)
        request_payload = request.model_dump(exclude_none=True, by_alias=True)
        request_payload["contract_id"] = cid
        if use_post:
            request_payload = with_method_override(request_payload, "PUT")
        self.logger.info("Updating template geo restriction post_fallback=%s", use_post)
        return await self._request(
            UPDATE_TEMPLATE_GEORESTRICTION,
            api_version=api_version,
            route_name="default" if use_post else "put",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "georestriction_id": require_identifier(
                    georestriction_id,
                    "georestriction_id",
                ),
            },
            json=request_payload,
            request_contract_id=cid,
        )

    async def delete_template_georestriction(
        self,
        *,
        template_id: str,
        georestriction_id: str,
        api_version: str | None = None,
        use_post: bool = False,
    ) -> TemplateGeoRestrictionDeleteResponse:
        """Удалить геоограничитель шаблона."""
        return await self._request(
            DELETE_TEMPLATE_GEORESTRICTION,
            api_version=api_version,
            route_name="post_override" if use_post else "default",
            path_params={
                "template_id": require_identifier(template_id, "template_id"),
                "georestriction_id": require_identifier(
                    georestriction_id,
                    "georestriction_id",
                ),
            },
            data=with_method_override(None, "DELETE") if use_post else None,
        )
