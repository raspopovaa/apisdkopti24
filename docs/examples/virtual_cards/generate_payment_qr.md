---
description: "Платёжная строка для оплаты по QR: пример client.virtual_cards.generate_payment_qr() с запросом, ответом и ошибками."
---

<!-- Сгенерировано scripts/generate_method_examples.py из examples/methods/virtual_cards.yaml. Не редактируйте вручную. -->

# Платёжная строка для оплаты по QR

`client.virtual_cards.generate_payment_qr()` · [справочник метода](../../methods/virtual_cards.md) · [исходный файл примера](https://github.com/raspopovaa/apisdkopti24/blob/main/examples/methods/virtual_cards/generate_payment_qr.py)

Получить платёжную строку по мобильному профилю карты. Приложение водителя показывает её как QR-код на кассе АЗС.

| HTTP | Маршрут | Изменяет данные | Тарифицируется | DEMO | Автоповтор |
|---|---|:---:|:---:|:---:|---|
| POST | `v2/cards/{card_id}/pay` | Да | Нет | Нет | Нет: при неясном результате проверьте состояние, а не повторяйте запрос |

!!! warning "Вызов изменяет данные"
    Проверяйте метод на DEMO-стенде. Запускаемый пример спрашивает подтверждение перед вызовом.

## Пример

```python
"""Платёжная строка для оплаты по QR: client.virtual_cards.generate_payment_qr().

Получить платёжную строку по мобильному профилю карты. Приложение водителя показывает её
как QR-код на кассе АЗС.

Запуск:
    1. Заполните .env: API_BASE_URL, API_KEY, API_LOGIN, API_PASSWORD,
       API_CONTRACT_ID.
    2. Замените условные значения ниже своими.
    3. python examples/methods/virtual_cards/generate_payment_qr.py

Разбор запроса, ответа и ошибок:
https://raspopovaa.github.io/apisdkopti24/latest/examples/virtual_cards/generate_payment_qr/
"""

from __future__ import annotations

import asyncio
import os

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

# Условные значения: замените своими.
CARD_ID = "90000008"


async def example(client: APIClient) -> None:
    response = await client.virtual_cards.generate_payment_qr(card_id=CARD_ID, pin="4815")
    qr = response.data
    print(f"Строка действует до {qr.end_date}, попыток оплаты: {qr.tries}")


async def main() -> None:
    answer = input("Вызов изменяет данные на реальном API. Продолжить? [yes/no] ")
    if answer.strip().lower() != "yes":
        return
    settings = ConnectionSettings.from_env()
    credentials = EnvironmentCredentialsProvider.from_env()
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        contract_id = os.getenv("API_CONTRACT_ID")
        if contract_id:
            client.select_contract(contract_id=contract_id)
        await example(client)


if __name__ == "__main__":
    asyncio.run(main())
```

### Параметры метода

| Параметр | Python-тип | Обязательный | По умолчанию | Описание |
|---|---|:---:|---|---|
| `card_id` | <code>str</code> | Да | — | ID карты (можно передать в заголовке запроса |
| `pin` | <code>str</code> | Да | — | PIN мобильного профиля карты из 4–8 цифр. Значение не должно попадать в логи. |
| `contract_id` | <code>str &#124; None</code> | Нет | `None` | Идентификатор договора. Для части методов может быть получен из активного контекста SDK. |
| `api_version` | <code>str &#124; None</code> | Нет | `None` | Версия API. Обычно определяется SDK автоматически. |

### Модели запроса

Перед отправкой SDK собирает параметры в модели ниже. Pydantic проверяет типы и ограничения; при ошибке запрос не отправляется.

#### [`PaymentQRRequest`](../../data-types/virtual_cards/PaymentQRRequest.md)

| Поле | Python-тип | Обязательное | Ограничения | Описание |
|---|---|:---:|---|---|
| `pin` | <code>str</code> | Да | шаблон: '^[0-9]{4,8}$' | Пин-код МПК |

## Что отправляет SDK

Запрос записан при запуске примера выше: это ровно то, что SDK отправляет на сервер. Секреты скрыты, строка запроса показана без URL-кодирования.

```http
POST /vip/v2/cards/90000008/pay HTTP/1.1
Host: api-demo.opti-24.ru
api_key: ***
session_id: ***
contract_id: 1-T000025
date_time: 2026-01-15 10:30:00
Content-Type: application/x-www-form-urlencoded

pin=***
```

| Поле | Где передаётся | Значение | Тип в запросе | Обязательное в API | Описание |
|---|---|---|---|:---:|---|
| `card_id` | путь | `90000008` | string | Да | Часть пути запроса: подставляется в маршрут вместо шаблона. |
| `pin` | форма | `***` | string | Да | Пин-код МПК |
| `contract_id` | заголовок | `1-T000025` | string | — | Договор в заголовке запроса. API принимает договор и так; SDK отправляет заголовок вместе с полем запроса. |

Значения в строке запроса и в форме передаются строками: `True` превращается в `"true"`, списки — в повторяющиеся поля. Заголовки `api_key`, `date_time` и `session_id` SDK добавляет сам; сессию он получает при первом вызове.

## Что возвращает API

SDK проверяет ответ моделью [`PaymentQRResponse`](../../data-types/virtual_cards/PaymentQRResponse.md).
Пример ответа условный, структура совпадает с моделью SDK..

```json
{
  "status": {
    "code": 200
  },
  "data": {
    "code": "PAYMENT-STRING-EXAMPLE",
    "end_date": 1788240000,
    "transaction_count": 0,
    "tries": 3
  },
  "timestamp": 1596024392
}
```

Вывод примера на этом ответе:

```text
Строка действует до 1788240000, попыток оплаты: 3
```

### Модели ответа

Модели ответа и путь к их полям в JSON.

#### [`PaymentQRResponse`](../../data-types/virtual_cards/PaymentQRResponse.md)

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `status` | `status` | <code>ResponseStatus</code> | Да | Статус ответа API |
| `data` | `data` | <code>PaymentQRData</code> | Да | Типизированные данные ответа API |
| `timestamp` | `timestamp` | <code>int &#124; None</code> | Нет | Метка времени ответа API |

#### [`PaymentQRData`](../../data-types/virtual_cards/PaymentQRData.md) · `data`

| Поле | Путь в JSON | Python-тип | Обязательное | Описание |
|---|---|---|:---:|---|
| `code` | `data.code` | <code>str</code> | Да | Платёжная строка в формате BER-TLV |
| `end_date` | `data.end_date` | <code>int</code> | Да | Срок жизни платёжной строки — Unix-время окончания действия (до 10 минут от выдачи); единицы выведены из примера ответа API |
| `transaction_count` | `data.transaction_count` | <code>int</code> | Да | Число проведённых транзакций |
| `tries` | `data.tries` | <code>int</code> | Да | Максимальное число попыток оплаты |

## Ошибки

Ошибки API, характерные для метода. Формат тела ответа — как у API; текст сообщения сервера условный. Исключение и его текст записаны при выполнении вызова в SDK.

### 403 · `AccessDeniedError`

**Почему:** Доступ к МПК запрещён. Оплата с неверными секретными значениями блокирует оплату по карте.

**Что делать:** Перевыпустите МПК через `update_mpc()`; блокировку снимает `reset_mpc()`.

Ответ API:

```json
{
  "status": {
    "code": 403,
    "errors": [
      {
        "type": "accessDenied",
        "message": "Доступ запрещён"
      }
    ]
  }
}
```

Что выбросит SDK (`str(error)`):

```text
AccessDeniedError: [403] Доступ запрещён при выполнении generate_payment_qr Сообщение сервера: Доступ запрещён. Подсказка: Проверьте api_key, доступ к объекту, ограничения по роли, IP и остаток запросов по тарифу.
```

### Ошибки до отправки запроса

SDK проверяет параметры до обращения к методу API: запрос метода не отправляется и не расходует лимит запросов.

```python
await client.virtual_cards.generate_payment_qr(card_id=CARD_ID, pin="abcd")
```

PIN состоит только из цифр. Исключение `pydantic.ValidationError`:

```text
1 validation error for PaymentQRRequest
pin
  Value error, pin должен содержать от 4 до 8 цифр [type=value_error]
```

### Общие ошибки

Любой вызов может завершиться и общими ошибками: `NotAuthenticatedError` (401 — SDK один раз авторизуется заново и повторяет запрос), `RateLimitError` (429/509), `ServerError` (5xx), `APIConnectionError`, `OperationTimeoutError`. Как их обрабатывать — в разделе [Ошибки и повторы](../../errors.md).

## Что важно знать

- Платёжная строка `code` — то же, что деньги на кассе: не сохраняйте её и не пишите в журналы.
- Строка действует до 10 минут. `end_date` — срок жизни строки; по примеру ответа API это Unix-время окончания (секунды). Проверяйте его перед показом и выпускайте новую строку после истечения срока.
- Число выпущенных кодов ограничено `tries`; когда `transaction_count` достигает `tries`, сервер сам перевыпускает МПК. Не сбрасывайте и не пересчитывайте счётчики на своей стороне.
- Договор методу не нужен; SDK передаёт его, только если он указан или выбран в сессии. Платёжная строка не попадает в `repr` ответа.
