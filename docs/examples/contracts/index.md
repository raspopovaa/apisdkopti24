---
description: "Учебные примеры: Договоры и документы"
---

# Договоры и документы

Баланс и реквизиты договора, платежи, счета, закрывающие документы и заказ новых карт.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Данные договора и баланс](get_contract_data.md) | GET `getPartContractData` | Нет | Да | Да |
| [Платежи по договору](get_payments.md) | GET `getPayments` | Нет | Да | Да |
| [Счета на оплату](get_invoices.md) | GET `invoices` | Нет | Нет | Да |
| [Заказ счёта на оплату](order_invoice.md) | POST `invoice` | Да | Нет | Нет |
| [Закрывающие документы](get_documents.md) | GET `documents` | Нет | Нет | Нет |
| [Отправка документов на email](order_documents_email.md) | POST `documents` | Да | Да | Нет |
| [Заказ новых карт](order_cards.md) | POST `orderCards` | Да | Да | Нет |
