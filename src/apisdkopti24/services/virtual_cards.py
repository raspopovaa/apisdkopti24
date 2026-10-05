from ..models.virtual_cards import (
    MPCActionResponse,
    MPCConfirmRequest,
    MPCInitRequest,
    MPCListResponse,
    MPCResetRequest,
    MPCResetType,
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
    """Методы для работы с виртуальными картами (ВК) и мобильными профилями карт (МПК)"""

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

    async def create_virtual_card(
        self,
        *,
        user_id: str | None = None,
        contract_id: str | None = None,
        template_id: str | None = None,
        api_version: str | None = None,
    ) -> VirtualCardResponse:
        """Выпуск виртуальной карты (POST /vip/v2/cards).

        Договор — явный ``contract_id``, иначе выбранный договор сессии. Без
        договора сервер выпустил бы карту на первый из договоров пользователя,
        поэтому SDK всегда передаёт договор. ``template_id`` можно не указывать,
        если шаблон ВК закреплён за пользователем через ``users.attach_contracts``.

        Метод платный, выпускает настоящую карту и не повторяется автоматически.
        """
        request = VirtualCardCreateRequest(user_id=user_id, template_id=template_id)
        cid = await self._resolve_contract_id(contract_id)
        request = request.model_copy(update={"contract_id": cid})
        self.logger.info("Выпуск виртуальной карты через POST /vip/v2/cards")
        return await self._request(
            CREATE_VIRTUAL_CARD,
            api_version=api_version,
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )

    async def release_virtual_card(
        self,
        *,
        type_: str | None = None,
        template_id: str | None = None,
        user_id: str | None = None,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> VirtualCardResponse:
        """Выпуск виртуальной карты (POST /vip/v2/cards/release).

        Укажите ровно один из параметров: ``type_`` (``limit`` или ``wallet``) или
        ``template_id`` (ID шаблона виртуальной карты). Дополнительно можно указать
        ``user_id`` (ID пользователя).

        Договор — явный ``contract_id``, иначе выбранный договор сессии: без
        договора сервер выпустил бы карту на первый из договоров пользователя.
        Метод платный, выпускает настоящую карту и не повторяется автоматически.

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
        cid = await self._resolve_contract_id(contract_id)
        request = request.model_copy(update={"contract_id": cid})

        self.logger.info("Выпуск виртуальной карты через /vip/v2/cards/release")
        return await self._request(
            RELEASE_VIRTUAL_CARD,
            api_version=api_version,
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )

    async def delete_mpc(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> SimpleActionResponse:
        """Удалить мобильный профиль карты (POST /vip/v2/cards/{card_id}/deleteMPC).

        Удаление нужно перед повторным ``init_mpc``: на карте может быть только
        один МПК. Метод не повторяется автоматически.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Удаление мобильного профиля карты")
        return await self._request(
            DELETE_MPC,
            api_version=api_version,
            path_params={"card_id": wire_card_id},
            contract_header=cid,
        )

    async def reset_mpc(
        self,
        *,
        card_id: str,
        type_: MPCResetType = "ResetCounterCode",
        contract_id: str | None = None,
        api_version: str | None = None,
    ) -> ResetMPCResponse:
        """Сбросить счётчики МПК (POST /vip/v2/cards/{card_id}/resetMPC).

        Снимает блокировку, которую сервер ставит после неверного SMS-кода при
        выпуске МПК или после оплаты с неверными секретными значениями. Тип
        счётчика — ``ResetCounterCode`` (по умолчанию) или ``ResetCounterMPC``;
        какой тип какую блокировку снимает, спецификация не уточняет.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = MPCResetRequest.model_validate({"type": type_})
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Сброс счётчиков мобильного профиля карты")
        return await self._request(
            RESET_MPC,
            api_version=api_version,
            path_params={"card_id": wire_card_id},
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

        Договор этому методу по спецификации не нужен: SDK передаёт его заголовком,
        только если ``contract_id`` указан явно или выбран в сессии.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        form = PaymentQRRequest(pin=pin).model_dump()
        cid = (
            require_identifier(contract_id, "contract_id")
            if contract_id is not None
            else self.contract_id
        )
        self.logger.info("Формирование платёжного QR-кода")
        return await self._request(
            GENERATE_PAYMENT_QR,
            api_version=api_version,
            path_params={"card_id": wire_card_id},
            form=form,
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
        """Инициализировать выпуск МПК (POST /vip/v2/cards/{card_id}/initMPC).

        Карта должна быть привязана к ``user_id``, а существующий МПК — удалён
        через ``delete_mpc``. На телефон пользователя придёт SMS-код для
        ``confirm_mpc``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = MPCInitRequest(
            user_id=user_id, pin=pin, device_id=device_id, device_name=device_name
        )
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Инициализация мобильного профиля карты")
        return await self._request(
            INIT_MPC,
            api_version=api_version,
            path_params={"card_id": wire_card_id},
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
        """Подтвердить выпуск МПК SMS-кодом (POST /vip/v2/cards/{card_id}/confirmMPC).

        Неверный код блокирует выпуск МПК; снимает блокировку ``reset_mpc``. SDK
        не повторяет подтверждение автоматически.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        form = MPCConfirmRequest(code=code).model_dump()
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Подтверждение мобильного профиля карты")
        return await self._request(
            CONFIRM_MPC,
            api_version=api_version,
            path_params={"card_id": wire_card_id},
            form=form,
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
        """Перевыпустить МПК (POST /vip/v2/cards/{card_id}/updateMPC).

        Без ``new_pin`` перевыпускаются ключи оплаты, с ``new_pin`` меняется и PIN.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = MPCUpdateRequest(pin=pin, new_pin=new_pin)
        cid = await self._resolve_contract_id(contract_id)
        self.logger.info("Обновление мобильного профиля карты")
        return await self._request(
            UPDATE_MPC,
            api_version=api_version,
            path_params={"card_id": wire_card_id},
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )
