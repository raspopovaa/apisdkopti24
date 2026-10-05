from decimal import Decimal
from typing import Literal

from ..errors import RequestValidationError
from ..models.ewallet import (
    MoveToCardResponse,
    MoveToContractResponse,
    SetCardProductResponse,
)
from ..operations import operation
from ..service_base import _BaseService
from ..utils import to_json_param
from ..validation import decimal_to_wire, require_identifier, validate_identifier_list

CardProduct = Literal["wallet", "limit"]
SET_CARD_PRODUCT = operation("set_card_product", SetCardProductResponse)
MOVE_TO_CARD = operation("move_to_card", MoveToCardResponse)
MOVE_TO_CONTRACT = operation("move_to_contract", MoveToContractResponse)


class EwalletService(_BaseService):
    """Методы для работы с электронными кошельками (Ewallet).

    Электронный кошелёк — это тип карты, обслуживание которой производится не из средств договора,
    а из отдельного кошелькового счёта. Пользователь может:
      • менять тип карты (лимитная ↔ электронный кошелёк);
      • переводить средства со счёта договора на кошелёк;
      • переводить средства обратно с кошелька на договор.
    """

    async def set_card_product(
        self,
        *,
        contract_id: str | None = None,
        card_ids: list[str],
        product: CardProduct,
        api_version: str | None = None,
    ) -> SetCardProductResponse:
        """Изменить тип карт: лимитная (``limit``) или электронный кошелёк (``wallet``).

        ``card_ids`` — список ID карт; одну карту передавайте списком из одного
        элемента. Без ``contract_id`` используется выбранный договор сессии.
        """
        normalized_card_ids = validate_identifier_list(card_ids, "card_ids")
        if product not in {"wallet", "limit"}:
            raise RequestValidationError("product должен быть равен 'wallet' или 'limit'")
        cid = await self._resolve_contract_id(contract_id)

        body = {
            "contract_id": cid,
            "card_id": to_json_param(normalized_card_ids),
            "product": product,
        }

        return await self._request(
            SET_CARD_PRODUCT,
            api_version=api_version,
            form=body,
            contract_header=cid,
        )

    async def move_to_card(
        self,
        *,
        contract_id: str | None = None,
        card_id: str,
        amount: Decimal,
        api_version: str | None = None,
    ) -> MoveToCardResponse:
        """Перевести деньги со счёта договора на электронный кошелёк карты.

        ``amount`` — сумма в рублях, не больше двух знаков после запятой. Без
        ``contract_id`` используется выбранный договор сессии.

        Типовой сценарий:
            Пополнить электронный кошелёк конкретной карты перед поездкой.
            Операция изменяет баланс и не должна повторяться вслепую после
            неопределённого сетевого результата.

        Пример вызова:
        ```python
        transfer = await client.ewallet.move_to_card(
            contract_id="contract-id",
            card_id="card-id",
            amount=Decimal("2500.00"),
        )
        ```

        Пример payload:
        ```json
        {"contract_id": "contract-id", "card_id": "card-id", "amount": "2500.00"}
        ```
        """
        wire_card_id = require_identifier(card_id, "card_id")
        wire_amount = decimal_to_wire(amount)
        cid = await self._resolve_contract_id(contract_id)

        body = {
            "contract_id": cid,
            "card_id": wire_card_id,
            "amount": wire_amount,
        }

        return await self._request(
            MOVE_TO_CARD,
            api_version=api_version,
            form=body,
            contract_header=cid,
        )

    async def move_to_contract(
        self,
        *,
        contract_id: str | None = None,
        card_id: str,
        amount: Decimal,
        api_version: str | None = None,
    ) -> MoveToContractResponse:
        """Перевести деньги с электронного кошелька карты обратно на договор.

        ``amount`` — сумма в рублях, не больше двух знаков после запятой. Без
        ``contract_id`` используется выбранный договор сессии.
        """
        wire_card_id = require_identifier(card_id, "card_id")
        wire_amount = decimal_to_wire(amount)
        cid = await self._resolve_contract_id(contract_id)

        body = {
            "contract_id": cid,
            "card_id": wire_card_id,
            "amount": wire_amount,
        }

        return await self._request(
            MOVE_TO_CONTRACT,
            api_version=api_version,
            form=body,
            contract_header=cid,
        )
