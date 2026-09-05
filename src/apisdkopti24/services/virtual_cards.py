from ..models.virtual_cards import (
    MPCActionResponse,
    MPCListResponse,
    PaymentQRResponse,
    ResetMPCResponse,
    SimpleActionResponse,
    VirtualCardResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..validation import require_identifier, validate_non_empty_value

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
            params={"contract_id": cid} if cid is not None else None,
            request_contract_id=cid,
        )

    # === Выпуск виртуальной карты (старый метод) ===
    async def create_virtual_card(
        self,
        *,
        user_id: str,
        api_version: str | None = None,
    ) -> VirtualCardResponse:
        """Выпуск виртуальной карты (старый метод POST /vip/v2/cards)"""
        payload = {"user_id": user_id}
        self.logger.info("Creating virtual card using legacy method")
        return await self._request(
            CREATE_VIRTUAL_CARD,
            api_version=api_version,
            data=payload,
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
            type_="wallet",
            template_id="template-id",
            user_id="user-id",
        )
        ```

        Пример payload:
        ```json
        {"type": "wallet", "template_id": "template-id", "user_id": "user-id"}
        ```
        """
        payload = {}
        if type_:
            payload["type"] = type_
        if template_id:
            payload["template_id"] = template_id
        if user_id:
            payload["user_id"] = user_id

        self.logger.info("Creating virtual card")
        return await self._request(
            RELEASE_VIRTUAL_CARD,
            api_version=api_version,
            data=payload,
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
            request_contract_id=cid,
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
        if type_ not in {"ResetCounterCode", "ResetCounterMPC"}:
            raise ValueError("type_ must be 'ResetCounterCode' or 'ResetCounterMPC'")
        payload = {"type": type_}
        self.logger.info("Resetting mobile card profile counters")
        return await self._request(
            RESET_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            data=payload,
            request_contract_id=cid,
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
            data={"pin": self._validate_pin(pin, "pin")},
            request_contract_id=cid,
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
        request_payload = {
            "user_id": require_identifier(user_id, "user_id"),
            "pin": self._validate_pin(pin, "pin"),
            "device_id": self._validate_length(device_id, "device_id", 1, 255),
            "device_name": self._validate_length(device_name, "device_name", 11, 17),
        }
        self.logger.info("Initializing mobile card profile")
        return await self._request(
            INIT_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            data=request_payload,
            request_contract_id=cid,
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
            data={"code": validate_non_empty_value(code, "code")},
            request_contract_id=cid,
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
        request_payload = {"pin": self._validate_pin(pin, "pin")}
        if new_pin is not None:
            request_payload["new_pin"] = self._validate_pin(new_pin, "new_pin")
        self.logger.info("Updating mobile card profile")
        return await self._request(
            UPDATE_MPC,
            api_version=api_version,
            path_params={"card_id": require_identifier(card_id, "card_id")},
            data=request_payload,
            request_contract_id=cid,
        )

    @staticmethod
    def _validate_pin(value: str, field_name: str) -> str:
        normalized = validate_non_empty_value(value, field_name)
        if not normalized.isdigit() or not 4 <= len(normalized) <= 8:
            raise ValueError(f"{field_name} must contain 4 to 8 digits")
        return normalized

    @staticmethod
    def _validate_length(value: str, field_name: str, minimum: int, maximum: int) -> str:
        normalized = validate_non_empty_value(value, field_name)
        if not minimum <= len(normalized) <= maximum:
            raise ValueError(f"{field_name} length must be between {minimum} and {maximum}")
        return normalized
