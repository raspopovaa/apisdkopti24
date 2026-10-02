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

| Поле | Тип после валидации | JSON-тип | Обязательное | `None` | По умолчанию | Описание | Ограничения схемы | Что проверяет Pydantic |
|---|---|---|:---:|:---:|---|---|---|---|
| `contract_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID договора | — | Значение преобразуется и проверяется как str. |
| `way_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID договора в процессинге | — | Значение преобразуется и проверяется как str. |
| `contract_number` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Номер договора | — | Значение преобразуется и проверяется как str. |
| `unique_payment_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Уникальный идентификатор платежа (УИП) | — | Значение преобразуется и проверяется как str. |
| `client` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID клиента | — | Значение преобразуется и проверяется как str. |
| `client_category` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Категория клиента | — | Значение преобразуется и проверяется как str. |
| `contract_category` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Категория договора | — | Значение преобразуется и проверяется как str. |
| `country` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Страна заключения | — | Значение преобразуется и проверяется как str. |
| `region` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Регион заключения | — | Значение преобразуется и проверяется как str. |
| `fin_institution` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Финансовый институт | — | Значение преобразуется и проверяется как str. |
| `invoice_scheme` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Подключение инвойсирования | — | Значение преобразуется и проверяется как str. |
| `invoice_period` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Дни выставления счетов | — | Значение должно соответствовать одному из типов: str, None |
| `invoice_pmt_delay` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Количество дней на оплату инвойса | — | Значение должно соответствовать одному из типов: str, None |
| `contract_status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID статуса договора | — | Значение преобразуется и проверяется как str. |
| `contract_status_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Значение статуса договора | — | Значение преобразуется и проверяется как str. |
| `pay_scheme` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Условия оплаты | — | Значение преобразуется и проверяется как str. |
| `discount_scheme` (в JSON также: <code>"discount_scheme "</code>) | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Схема расчета скидки (код из справочника DiscountScheme) | — | Значение преобразуется и проверяется как str. |
| `auto_pay` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Признак разрешения для подключения автосписания с р/с | — | Значение преобразуется и проверяется как str. |
| `auto_pay_type` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип подключения автоматического платежа | — | Значение преобразуется и проверяется как str. |
| `credit_limit` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Кредитный лимит | — | Значение должно соответствовать одному из типов: str, None |
| `current_amount_limiter` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Накопленная сумма по контракту | — | Значение преобразуется и проверяется как str. |
| `balance_amount_limiter` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Доступная сумма по контракту (max – current) | — | Значение должно соответствовать одному из типов: str, None |
| `max_amount_limiter` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | Ограничение лимита на сумму договора | — | Значение должно соответствовать одному из типов: str, None |
| `date_open` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата заключения договора | — | Значение преобразуется и проверяется как str. |
| `effective_date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата вступления в силу | — | Значение преобразуется и проверяется как str. |
| `end_date` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата окончания | — | Значение преобразуется и проверяется как str. |
| `date_expire` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Дата закрытия | — | Значение преобразуется и проверяется как str. |
| `product_type` (в JSON также: <code>"product_type "</code>) | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | Признак универсального топливного продукта (false – старый продукт, true – УТП) | — | Значение преобразуется и проверяется как bool. |
| `type_code` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Тип договора | — | Значение преобразуется и проверяется как str. |
| `supplier_name` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Имя поставщика | — | Значение преобразуется и проверяется как str. |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.
