from ..models.virtual_cards import (
    MPCActionResponse,
    MPCConfirmRequest,
    MPCInitRequest,
    MPCListResponse,
    MPCResetRequest,
    MPCUpdateRequest,
    PaymentQRRequest,
    PaymentQRResponse,
    ResetMPCResponse,
    SimpleActionResponse,
    VirtualCardCreateRequest,
    VirtualCardReleaseRequest,
    VirtualCardResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import require_identifier

GET_MPC_QR_LIST = operation("get_mpc_qr_list", MPCListResponse)
CREATE_VIRTUAL_CARD = operation("create_virtual_card", VirtualCardResponse)
RELEASE_VIRTUAL_CARD = operation("release_virtual_card", VirtualCardResponse)
DELETE_MPC = operation("delete_mpc", SimpleActionResponse)
RESET_MPC = operation("reset_mpc", ResetMPCResponse)
GENERATE_PAYMENT_QR = operation("generate_payment_qr", PaymentQRResponse)
INIT_MPC = operation("init_mpc", MPCActionResponse)
CONFIRM_MPC = operation("confirm_mpc", MPCActionResponse)
UPDATE_MPC = operation("update_mpc", MPCActionResponse)


class VirtualCardsService(_BaseService):
    """
    Методы для работы с виртуальными картами (ВК) и мобильными профилями карт (МПК)
    """

    async def get_mpc_qr_list(
        self,
        *,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> MPCListResponse:
        """Получить список выпущенных МПК/QR (GET /vip/v2/MPC)."""
        cid = require_identifier(contract_id, "contract_id") if contract_id is not None else None
        self.logger.info("Получение списка выпущенных МПК/QR")
        return await self._request(
            GET_MPC_QR_LIST,
            api_version=api_version,
            query={"contract_id": cid} if cid is not None else None,
            contract_header=cid,
        )

    # === Выпуск виртуальной карты (старый метод) ===
    async def create_virtual_card(
        self,
        *,
        user_id: str | None = None,
        contract_id: str | None = None,
        template_id: str | None = None,
        api_version: str | None = None,
    ) -> VirtualCardResponse:
        """Выпуск виртуальной карты (старый метод POST /vip/v2/cards)"""
        cid = require_identifier(contract_id, "contract_id") if contract_id is not None else None
        request = VirtualCardCreateRequest(
            user_id=user_id, contract_id=cid, template_id=template_id
        )
        self.logger.info("Creating virtual card using legacy method")
        return await self._request(
            CREATE_VIRTUAL_CARD,
            api_version=api_version,
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )

    # === Выпуск виртуальной карты (новый метод /release) ===
    async def release_virtual_card(
        self,
        *,
        type_: str | None = None,
        template_id: str | None = None,
        user_id: str | None = None,
        api_version: str | None = None,
    ) -> VirtualCardResponse:
        """
        Выпуск виртуальной карты (новый метод /vip/v2/cards/release)
        Можно указать:
        - type (например, "wallet")
        - template_id (ID шаблона ВК)
        - user_id (ID пользователя)

        Типовой сценарий:
            Выпустить карту пользователю по заранее настроенному шаблону лимитов
            и ограничений.

        Пример вызова:
        ```python
        card = await client.virtual_cards.release_virtual_card(
            template_id="template-id",
            user_id="user-id",
        )
        ```

        Пример payload:
        ```json
        {"template_id": "template-id", "user_id": "user-id"}
        ```
        """
        request = VirtualCardReleaseRequest.model_validate(
            {"type": type_, "template_id": template_id, "user_id": user_id}
        )

        self.logger.info("Creating virtual card")
        return await self._request(
            RELEASE_VIRTUAL_CARD,
            api_version=api_version,
            form=request.model_dump(exclude_none=True),
        )

    # === Удаление МПК ===
    async def delete_mpc(
        self,
        card_id: str,
        api_version: str | None = None,
        *,
        contract_id: str | None = None,
    ) -> SimpleActionResponse:
        """Удаление мобильного профиля карты (МПК)"""
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Deleting mobile card profile")
        return await self._request(
            DELETE_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            contract_header=cid,
        )

    # === Сброс счётчиков МПК ===
    async def reset_mpc(
        self,
        card_id: str,
        type_: str = "ResetCounterCode",
        api_version: str | None = None,
        *,
        contract_id: str | None = None,
    ) -> ResetMPCResponse:
        """
        Сброс счётчиков МПК (POST /vip/v2/cards/{card_id}/resetMPC)
        Тип счетчика (ResetCounterCode/ResetCounterMPC,
        по-умолчанию, если не вызывать, вызывается ResetCounterCode)
        """
        cid = await self._resolve_contract_id(contract_id)
        request = MPCResetRequest.model_validate({"type": type_})
        self.logger.info("Resetting mobile card profile counters")
        return await self._request(
            RESET_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            form=request.model_dump(),
            contract_header=cid,
        )

    async def generate_payment_qr(
        self,
        *,
        card_id: str,
        pin: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> PaymentQRResponse:
        """Получить платёжную строку для формирования одноразового QR-кода.

        API возвращает BER-TLV строку, а не изображение. Приложение должно
        отобразить ``response.code`` как QR и прекратить его использование не
        позднее ``response.end_date``.
        """
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Generating payment QR")
        return await self._request(
            GENERATE_PAYMENT_QR,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            form=PaymentQRRequest(pin=pin).model_dump(),
            contract_header=cid,
        )

    async def init_mpc(
        self,
        *,
        card_id: str,
        user_id: str,
        pin: str,
        device_id: str,
        device_name: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> MPCActionResponse:
        """Инициализировать выпуск МПК (POST /vip/v2/cards/{card_id}/initMPC)."""
        cid = await self._resolve_contract_id(contract_id)
        request = MPCInitRequest(
            user_id=user_id, pin=pin, device_id=device_id, device_name=device_name
        )
        self.logger.info("Initializing mobile card profile")
        return await self._request(
            INIT_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            form=request.model_dump(),
            contract_header=cid,
        )

    async def confirm_mpc(
        self,
        *,
        card_id: str,
        code: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> MPCActionResponse:
        """Подтвердить выпуск МПК (POST /vip/v2/cards/{card_id}/confirmMPC)."""
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Confirming mobile card profile")
        return await self._request(
            CONFIRM_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            form=MPCConfirmRequest(code=code).model_dump(),
            contract_header=cid,
        )

    async def update_mpc(
        self,
        *,
        card_id: str,
        pin: str,
        new_pin: str | None = None,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> MPCActionResponse:
        """Обновить МПК (POST /vip/v2/cards/{card_id}/updateMPC)."""
        cid = await self._resolve_contract_id(contract_id)
        request = MPCUpdateRequest(pin=pin, new_pin=new_pin)
        self.logger.info("Updating mobile card profile")
        return await self._request(
            UPDATE_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )
