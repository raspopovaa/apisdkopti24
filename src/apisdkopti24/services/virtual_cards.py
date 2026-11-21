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
    ) -> MPCListResponse:
        """Получить список выпущенных МПК/QR (операция ``GET_MPC_QR_LIST``).

        Аргументы проверяются до сети.

        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :return: ``MPCListResponse``: ``response.result`` (элементы) и ``response.total_count``
            (всего по запросу).
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid = require_identifier(contract_id, "contract_id") if contract_id is not None else None
        return await self._request(
            GET_MPC_QR_LIST,
            query={"contract_id": cid} if cid is not None else None,
            contract_header=cid,
        )

    async def create_virtual_card(
        self,
        *,
        user_id: str | None = None,
        contract_id: str | None = None,
        template_id: str | None = None,
    ) -> VirtualCardResponse:
        """Выпуск виртуальной карты (операция ``CREATE_VIRTUAL_CARD``).

        Аргументы проверяются до сети.

        Договор: явный ``contract_id``, иначе выбранный договор сессии. Без
        договора сервер выпустил бы карту на первый из договоров пользователя,
        поэтому SDK всегда передаёт договор. ``template_id`` можно не указывать,
        если шаблон ВК закреплён за пользователем через ``users.attach_contracts``.

        Метод платный, выпускает настоящую карту и не повторяется автоматически.

        :param user_id: Идентификатор пользователя.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :param template_id: Идентификатор шаблона.
        :return: ``VirtualCardResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid, request = await self._validated_with_contract(
            VirtualCardCreateRequest,
            contract_id,
            {"user_id": user_id, "template_id": template_id},
        )
        return await self._request(
            CREATE_VIRTUAL_CARD,
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
    ) -> VirtualCardResponse:
        """Выпуск виртуальной карты (операция ``RELEASE_VIRTUAL_CARD``).

        Аргументы проверяются до сети.

        Укажите ровно один из параметров: ``type_`` (``limit`` или ``wallet``) или
        ``template_id`` (ID шаблона виртуальной карты). Дополнительно можно указать
        ``user_id`` (ID пользователя).

        Договор: явный ``contract_id``, иначе выбранный договор сессии: без
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

        :param type_: Тип карты: ``limit`` — лимитная схема, ``wallet`` — электронный кошелёк.
            Обязателен, если не указан ``template_id``; не передаётся, если указан
            ``template_id``.
        :param template_id: Идентификатор шаблона.
        :param user_id: Идентификатор пользователя.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``VirtualCardResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        cid, request = await self._validated_with_contract(
            VirtualCardReleaseRequest,
            contract_id,
            {"type": type_, "template_id": template_id, "user_id": user_id},
        )
        return await self._request(
            RELEASE_VIRTUAL_CARD,
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )

    async def delete_mpc(
        self,
        *,
        card_id: str,
        contract_id: str | None = None,
    ) -> SimpleActionResponse:
        """Удалить мобильный профиль карты (операция ``DELETE_MPC``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Удаление нужно перед повторным ``init_mpc``: на карте может быть только
        один МПК. Метод не повторяется автоматически.

        :param card_id: Идентификатор топливной карты.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``SimpleActionResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            DELETE_MPC,
            path_params={"card_id": wire_card_id},
            contract_header=cid,
        )

    async def reset_mpc(
        self,
        *,
        card_id: str,
        type_: MPCResetType = "ResetCounterCode",
        contract_id: str | None = None,
    ) -> ResetMPCResponse:
        """Сбросить счётчики МПК (операция ``RESET_MPC``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Снимает блокировку, которую сервер ставит после неверного SMS-кода при
        выпуске МПК или после оплаты с неверными секретными значениями. Тип
        счётчика: ``ResetCounterCode`` (по умолчанию) или ``ResetCounterMPC``;
        какой тип какую блокировку снимает, спецификация не уточняет.

        :param card_id: Идентификатор топливной карты.
        :param type_: ``ResetCounterCode`` сбрасывает блокировку оплаты, ``ResetCounterMPC`` —
            блокировку выпуска МПК.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``ResetMPCResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = MPCResetRequest.model_validate({"type": type_})
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            RESET_MPC,
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
    ) -> PaymentQRResponse:
        """Получить платёжную строку для формирования одноразового QR-кода.

        Операция ``GENERATE_PAYMENT_QR``. Аргументы проверяются до сети.

        API возвращает BER-TLV строку, а не изображение. Приложение должно
        отобразить ``response.code`` как QR и прекратить его использование не
        позднее ``response.end_date``.

        Договор этому методу по спецификации не нужен: SDK передаёт его заголовком,
        только если ``contract_id`` указан явно или выбран в сессии.

        :param card_id: Идентификатор топливной карты.
        :param pin: PIN мобильного профиля карты из 4–8 цифр. Значение не должно попадать в
            логи.
        :param contract_id: Идентификатор договора. Для части методов может быть получен из
            активного контекста SDK.
        :return: ``PaymentQRResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку. Запрос не отправлен.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        form = PaymentQRRequest(pin=pin).model_dump()
        cid = (
            require_identifier(contract_id, "contract_id")
            if contract_id is not None
            else self.contract_id
        )
        return await self._request(
            GENERATE_PAYMENT_QR,
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
    ) -> MPCActionResponse:
        """Инициализировать выпуск МПК (операция ``INIT_MPC``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Карта должна быть привязана к ``user_id``, а существующий МПК: удалён
        через ``delete_mpc``. На телефон пользователя придёт SMS-код для
        ``confirm_mpc``.

        :param card_id: Идентификатор топливной карты.
        :param user_id: ID пользователя, к которому привязана карта.
        :param pin: Новый PIN мобильного профиля из 4–8 цифр.
        :param device_id: Идентификатор устройства длиной 1–255 символов.
        :param device_name: Название устройства длиной 11–17 символов.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``MPCActionResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = MPCInitRequest(
            user_id=user_id, pin=pin, device_id=device_id, device_name=device_name
        )
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            INIT_MPC,
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
    ) -> MPCActionResponse:
        """Подтвердить выпуск МПК SMS-кодом (операция ``CONFIRM_MPC``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Неверный код блокирует выпуск МПК; снимает блокировку ``reset_mpc``. SDK
        не повторяет подтверждение автоматически.

        :param card_id: Идентификатор топливной карты.
        :param code: Код подтверждения выпуска МПК из SMS.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``MPCActionResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        form = MPCConfirmRequest(code=code).model_dump()
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            CONFIRM_MPC,
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
    ) -> MPCActionResponse:
        """Перевыпустить МПК (операция ``UPDATE_MPC``).

        Договор: явный ``contract_id`` или договор сессии. Аргументы проверяются до сети.

        Без ``new_pin`` перевыпускаются ключи оплаты, с ``new_pin`` меняется и PIN.

        :param card_id: Идентификатор топливной карты.
        :param pin: Текущий PIN мобильного профиля из 4–8 цифр.
        :param new_pin: Новый PIN из 4–8 цифр. Если не передан, API перевыпускает ключи оплаты
            без смены PIN.
        :param contract_id: ID договора. Если не передан, берётся договор сессии.
        :return: ``MPCActionResponse``, данные в ``response.data``.
        :raises RequestValidationError: Аргумент не прошёл проверку или договор не выбран.
            Запрос не отправлен.
        :raises ContractSelectionError: Договор не передан, у логина их несколько, и ни один не
            выбран через ``client.select_contract()``.
        :raises Opti24Error: Ошибка API, сети или разбора ответа; подклассы описаны в
            ``docs/errors.md``.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        request = MPCUpdateRequest(pin=pin, new_pin=new_pin)
        cid = await self._resolve_contract_id(contract_id)
        return await self._request(
            UPDATE_MPC,
            path_params={"card_id": wire_card_id},
            form=request.model_dump(exclude_none=True),
            contract_header=cid,
        )
