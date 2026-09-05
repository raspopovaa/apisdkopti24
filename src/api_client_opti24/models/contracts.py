from ..modeling import APIEnvelope, BaseModel, Field


# ==========================
# Информация по договору
# ==========================
class BalanceData(BaseModel):
    """Данные по расходу и балансу договора"""

    available_amount: str = Field(..., description="Доступный остаток")
    own_balance: str = Field(..., description="Собственные средства")
    balance: str = Field(..., description="Собственные средства клиента с учетом блокировок")
    consumption_for_month: str = Field(
        ..., description="Расход в текущем месяце (в валюте контракта)"
    )
    consumption_for_month_volume: str = Field(
        ..., description="Объем потребления в текущем месяце (в литрах)"
    )
    consumption_for_prev_month_volume: str = Field(
        ..., description="Объем потребления в предыдущем месяце (в литрах)"
    )
    last_payment_sum: str | None = Field(None, description="Сумма последнего платежа")
    last_payment_date: str | None = Field(None, description="Дата последнего платежа")
    currency: str = Field(..., description="Валюта договора")


class ContractData(BaseModel):
    """Основные данные договора"""

    contract_id: str = Field(..., description="ID договора")
    way_id: str = Field(..., description="ID договора в процессинге")
    contract_number: str = Field(..., description="Номер договора")
    unique_payment_id: str = Field(..., description="Уникальный идентификатор платежа (УИП)")
    client: str = Field(..., description="ID клиента")
    client_category: str = Field(..., description="Категория клиента")
    contract_category: str = Field(..., description="Категория договора")
    country: str = Field(..., description="Страна заключения")
    region: str = Field(..., description="Регион заключения")
    fin_institution: str = Field(..., description="Финансовый институт")
    invoice_scheme: str = Field(..., description="Подключение инвойсирования")
    invoice_period: str | None = Field(None, description="Дни выставления счетов")
    invoice_pmt_delay: str | None = Field(None, description="Количество дней на оплату инвойса")
    contract_status: str = Field(..., description="ID статуса договора")
    contract_status_name: str = Field(..., description="Значение статуса договора")
    pay_scheme: str = Field(..., description="Условия оплаты")
    discount_scheme: str = Field(
        ..., description="Схема расчета скидки (код из справочника DiscountScheme)"
    )
    auto_pay: str = Field(..., description="Признак разрешения для подключения автосписания с р/с")
    auto_pay_type: str = Field(..., description="Тип подключения автоматического платежа")
    credit_limit: str | None = Field(None, description="Кредитный лимит")
    current_amount_limiter: str = Field(..., description="Накопленная сумма по контракту")
    balance_amount_limiter: str | None = Field(
        None, description="Доступная сумма по контракту (max – current)"
    )
    max_amount_limiter: str | None = Field(None, description="Ограничение лимита на сумму договора")
    date_open: str = Field(..., description="Дата заключения договора")
    effective_date: str = Field(..., description="Дата вступления в силу")
    end_date: str = Field(..., description="Дата окончания")
    date_expire: str = Field(..., description="Дата закрытия")
    product_type: bool = Field(
        ...,
        description="Признак универсального топливного продукта (false – старый продукт, true – УТП)",
    )
    type_code: str = Field(..., description="Тип договора")
    supplier_name: str = Field(..., description="Имя поставщика")


class ManagerData(BaseModel):
    """Данные менеджера по сопровождению договора"""

    email: str = Field(..., description="Email менеджера")
    first_name: str = Field(..., description="Имя менеджера")
    last_name: str = Field(..., description="Фамилия менеджера")
    middle_name: str | None = Field(None, description="Отчество менеджера")
    work_phone: str | None = Field(None, description="Рабочий телефон менеджера")


class CardsData(BaseModel):
    """Информация по картам договора"""

    cards_quantity_all: str = Field(..., description="Число карт договора")
    cards_quantity_active: str = Field(..., description="Число активных карт договора")
    card_groups_quantity_all: str | None = Field(None, description="Число групп карт на договоре")


class ContractResponse(BaseModel):
    """Полный ответ API по договору"""

    mpc: bool = Field(..., description="Разрешен ли выпуск виртуальных карт")
    template_id: str | None = Field(None, description="ID шаблона виртуальных карт")
    status: str = Field(..., description="Статус Way4")
    status_crm: str = Field(..., description="Статус CRM")
    payment_term_id: str | None = Field(None, description="ID справочника условия оплаты")
    payment_scheme_id: str | None = Field(None, description="ID справочника схема оплаты")
    is_dealer: bool = Field(..., description="Признак дилерский")
    balanceData: BalanceData = Field(..., description="Данные по расходу и балансу договора")
    contractData: ContractData = Field(..., description="Данные договора")
    managerData: ManagerData | None = Field(None, description="Данные по менеджеру договора")
    cardsData: CardsData = Field(
        ..., description="Данные по количеству карт и групп карт на договоре"
    )


class ContractDataResponse(APIEnvelope[ContractResponse]):
    """Полный envelope ответа метода получения данных договора."""


# ==========================
# Платежи по договору
# ==========================
class PaymentItem(BaseModel):
    """Информация об одном платеже по договору."""

    id: str = Field(..., description="Идентификатор платежа")
    contract_id: str = Field(..., description="ID договора, к которому относится платёж")
    date: str = Field(
        ...,
        description="Дата и время платежа в формате ISO 8601 (например, 2015-04-15T15:25:20)",
    )
    amount: str = Field(..., description="Сумма платежа в валюте договора")
    currency: str = Field(..., description="Код валюты и её обозначение, например '810;RUR'")
    amount_client: str = Field(..., description="Сумма, поступившая клиенту")
    description: str = Field(..., description="Описание или назначение платежа")
    payment_name: str = Field(
        ...,
        description="Наименование типа платежа, например 'Payment To Client Contract'",
    )
    payment_type: str = Field(..., description="Тип платежа, например 'P;Advice'")
    payment_number: str = Field(..., description="Номер платёжного документа")


class PaymentsData(BaseModel):
    """Секция data из ответа API, содержит список платежей и их количество."""

    total_count: int = Field(..., description="Количество найденных платежей")
    result: list[PaymentItem] = Field(..., description="Список платежей по договору")


class PaymentsResponse(APIEnvelope[PaymentsData]):
    """Основная модель ответа метода /getPayments."""


# ==========================
# Получение списка документов
# ==========================
class DocumentItem(BaseModel):
    """Информация об одном первичном документе."""

    id: str = Field(..., description="Уникальный идентификатор документа (UUID)")
    name: str = Field(..., description="Название документа, например 'УПД'")
    name_doc: str = Field(
        ..., description="Системное имя документа, например 'СчетФактураВыданный'"
    )
    number: str = Field(..., description="Номер документа, например 'CSC0000000533998'")
    date: int = Field(..., description="Дата документа в формате UNIX timestamp")
    total: float = Field(..., description="Общая сумма документа")
    vat: float = Field(..., description="Сумма НДС")
    sum: float = Field(..., description="Сумма без НДС")
    currency: str = Field(..., description="Валюта документа, например 'руб.'")
    consignee: str = Field(..., description="Грузополучатель (организация)")
    contract_id: str = Field(..., description="ID договора, к которому относится документ")
    contract_name: str = Field(..., description="Номер или название договора")


class DocumentsData(BaseModel):
    """Секция 'data' в ответе метода /documents."""

    total_count: int = Field(..., description="Количество найденных документов")
    result: list[DocumentItem] = Field(..., description="Список найденных документов")


class DocumentsResponse(APIEnvelope[DocumentsData]):
    """Ответ метода GET /v2/documents."""


# ==========================
# Заказ документов на email
# ==========================


class DocumentsOrderResponse(APIEnvelope[bool]):
    """Ответ метода POST /v2/documents (заказ документов)."""


# ==========================
# ЗАКАЗ ТОПЛИВНЫХ КАРТ
# ==========================


class OrderCardsResponse(APIEnvelope[bool]):
    """Ответ метода POST /v2/orderCards."""


# ==========================
# ЗАКАЗ СЧЁТА НА ОПЛАТУ
# ==========================


class InvoiceOrderResponse(APIEnvelope[bool]):
    """Ответ метода POST /v2/invoice."""


# ==========================
# СПИСОК СЧЁТОВ НА ОПЛАТУ
# ==========================
class InvoiceItem(BaseModel):
    """Информация об одном счёте на оплату."""

    id: str = Field(..., description="Уникальный идентификатор счёта")
    contract_id: str = Field(..., description="ID договора, к которому относится счёт")
    ref_number: str = Field(..., description="Номер счёта, указанный в системе")
    date_start: str = Field(..., description="Дата начала периода счёта (YYYY-MM-DD)")
    date_end: str = Field(..., description="Дата окончания периода счёта (YYYY-MM-DD)")
    last_update: str = Field(
        ..., description="Дата и время последнего обновления счёта (ISO формат)"
    )
    currency: str = Field(..., description="Код валюты, например '810'")
    amount: str = Field(..., description="Сумма счёта")
    paid_amount: str = Field(..., description="Оплаченная сумма")
    status: str = Field(..., description="Статус счёта, например 'OPEN' или 'PAID'")
    comment: str = Field(..., description="Комментарий к счёту, например 'Intermediate Invoice'")


class InvoicesData(BaseModel):
    """Секция 'data' в ответе списка счетов."""

    total_count: int = Field(..., description="Количество найденных счетов")
    result: list[InvoiceItem] = Field(..., description="Список счетов на оплату")


class InvoicesResponse(APIEnvelope[InvoicesData]):
    """Ответ метода GET /v2/invoices."""
