---
description: "Полный ответ API по договору"
---
# `ContractResponse`

Полный ответ API по договору

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
| `mpc` | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | Разрешен ли выпуск виртуальных карт | — | Значение преобразуется и проверяется как bool. |
| `template_id` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | ID шаблона виртуальных карт | — | Значение преобразуется и проверяется как str. |
| `status` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Статус Way4 | — | Значение преобразуется и проверяется как str. |
| `status_crm` | <code>str</code> | <code>string</code> | Да | Нет | <code>—</code> | Статус CRM | — | Значение преобразуется и проверяется как str. |
| `payment_term_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID справочника условия оплаты | — | Значение должно соответствовать одному из типов: str, None |
| `payment_scheme_id` | <code>str &#124; None</code> | <code>string &#124; null</code> | Нет | Да | <code>None</code> | ID справочника схема оплаты | — | Значение должно соответствовать одному из типов: str, None |
| `is_dealer` (в JSON также: <code>Is_dealer</code>) | <code>bool</code> | <code>boolean</code> | Да | Нет | <code>—</code> | Признак дилерский | — | Значение преобразуется и проверяется как bool. |
| `balanceData` | <code>BalanceData</code> | <code>object (BalanceData)</code> | Да | Нет | <code>—</code> | Данные по расходу и балансу договора | — | Вложенный объект рекурсивно проверяется моделью BalanceData. |
| `contractData` | <code>ContractData</code> | <code>object (ContractData)</code> | Да | Нет | <code>—</code> | Данные договора | — | Вложенный объект рекурсивно проверяется моделью ContractData. |
| `managerData` | <code>ManagerData</code> | <code>object (ManagerData)</code> | Да | Нет | <code>—</code> | Данные по менеджеру договора | — | Вложенный объект рекурсивно проверяется моделью ManagerData. |
| `cardsData` | <code>CardsData</code> | <code>object (CardsData)</code> | Да | Нет | <code>—</code> | Данные по количеству карт и групп карт на договоре | — | Вложенный объект рекурсивно проверяется моделью CardsData. |

!!! note "Граница проверки"
    Значения, упомянутые только в тексте описания, не считаются жёстким ограничением. Например, фраза «Y или N» проверяется только тогда, когда в модели задан `Literal`, Enum, ограничение `Field` или пользовательский валидатор.

## Вложенные модели

- [`BalanceData`](BalanceData.md)
- [`ContractData`](ContractData.md)
- [`ManagerData`](ManagerData.md)
- [`CardsData`](CardsData.md)
