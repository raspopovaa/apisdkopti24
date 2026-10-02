---
description: "Основные данные договора"
---
# `ContractData`

Основные данные договора

!!! info "Назначение Pydantic"
    Тип модели: **response/data**. Ответ API проверяется этой моделью напрямую или рекурсивно как часть родительской response-модели. При несовпадении типов или отсутствии обязательного поля Pydantic формирует `ValidationError`.

## Поведение модели

| Настройка | Значение | Фактическое поведение |
|---|---|---|
| Дополнительные поля (`extra`) | `allow` | Дополнительные поля разрешены и сохраняются в модели. |
| Проверка default | `True` | Значения по умолчанию также проходят валидацию. |
| Заполнение по имени поля | `True` | Разрешено использовать имя поля наряду с alias. |
| Число → строка | `False` | Для строковых полей числовые значения могут быть преобразованы в строку. |

## Поля и проверки

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Alias | Ограничения схемы | Что проверяет Pydantic | Описание |
|---|---|---|:---:|:---:|---|---|---|---|---|
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID договора |
| `way_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID договора в процессинге |
| `contract_number` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Номер договора |
| `unique_payment_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Уникальный идентификатор платежа (УИП) |
| `client` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID клиента |
| `client_category` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Категория клиента |
| `contract_category` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Категория договора |
| `country` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Страна заключения |
| `region` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Регион заключения |
| `fin_institution` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Финансовый институт |
| `invoice_scheme` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Подключение инвойсирования |
| `invoice_period` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Дни выставления счетов |
| `invoice_pmt_delay` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Количество дней на оплату инвойса |
| `contract_status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | ID статуса договора |
| `contract_status_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Значение статуса договора |
| `pay_scheme` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Условия оплаты |
| `discount_scheme` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Схема расчета скидки (код из справочника DiscountScheme) |
| `auto_pay` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Признак разрешения для подключения автосписания с р/с |
| `auto_pay_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип подключения автоматического платежа |
| `credit_limit` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Кредитный лимит |
| `current_amount_limiter` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Накопленная сумма по контракту |
| `balance_amount_limiter` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Доступная сумма по контракту (max – current) |
| `max_amount_limiter` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | <code>—</code> | — | Значение должно соответствовать одному из типов: str, None | Ограничение лимита на сумму договора |
| `date_open` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Дата заключения договора |
| `effective_date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Дата вступления в силу |
| `end_date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Дата окончания |
| `date_expire` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Дата закрытия |
| `product_type` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как bool. | Признак универсального топливного продукта (false – старый продукт, true – УТП) |
| `type_code` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Тип договора |
| `supplier_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | <code>—</code> | — | Значение преобразуется и проверяется как str. | Имя поставщика |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.
