# Матрица моделей API

Матрица сформирована из спецификаций корпоративного API 1.1.60 и QR API 1.0.4. Значение `conditional` означает условную обязательность, описанную в соседней колонке.

## `attach_card`

`POST /v2/users/{user_id}/attachCard`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | form | `string` | True | ID карты |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `attach_contracts`

`POST /v2/users/{user_id}/attachContracts`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `sid` | json | `string` | True | ID договора |
| `template_id` | json | `string` | False | ID шаблона ВК |
| `use_mpc` | json | `bool` | False | Разрешен ли выпуск МПК (true/false) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `auth_user`

`POST /v1/authUser`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `login` | form | `string` | True | Логин пользователя |
| `password` | form | `string` | True | Пароль пользователя, захешированный функцией SHA-512 по стандарту SHS - FIPS 180-4, результат хеширования в нижнем регистре |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.client_id` | `string` | True | ID клиента |
| `data.client_status` | `string` | True | Статус пользователя |
| `data.org_name` | `string` | True | Название организации |
| `data.session_id` | `string` | True | ID текущей сессии пользователя |
| `data.user_id` | `string` | True | ID пользователя |
| `data.contracts` | `json` | True | Данные договоров доступных пользователю |
| `data.role_id` | `string` | True | ID роли пользователя |
| `data.role_name` | `string` | True | Название роли пользователя |
| `data.read_only` | `bool` | True | Режим чтения |
| `data.user_name` | `string` | False | Имя пользователя |
| `data.user_patronymic` | `string` | False | Отчество пользователя |
| `data.user_surname` | `string` | False | Фамилия пользователя |
| `data.last_contract` | `string` | False | Последний используемый договор |
| `data.access` | `json` | True | Доступ в ЛК/МП/API |
| `data.email` | `string` | True | Email |
| `data.phone` | `string` | False | Телефон |
| `data.access.web` | `bool` | True | Доступ ЛК |
| `data.access.api` | `bool` | True | Доступ API |
| `data.access.mobile` | `bool` | True | Доступ МП |
| `data.contracts[].id` | `string` | True | ID договора |
| `data.contracts[].number` | `string` | True | Номер договора |
| `data.contracts[].mpc` | `bool` | True | Возможность выпуска МПК |
| `data.contracts[].template_id` | `string` | False | ID шаблона ВК |
| `data.contracts[].cards_count` | `uint` | True | Количество топливных карт на договоре |
| `data.contracts[].one_price` | `bool` | True | Единая цена |

## `block_card`

`POST /v1/blockCard`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID контракта |
| `card_id` | form | `[string, string]` | True | ID карт |
| `block` | form | `bool` | True | true – блокировка, false – разблокировка |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `[string, string]` | False | ID карт, которые были заблокированы/разблокированы |

## `check_purchase`

`POST /v2/cards/{card_id}/checkPurchase`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) |
| `poi_id` | form | `string` | True | ID Точки обслуживания |
| `goods` | form | `array` | True | Массив данных о продукте |
| `goods[].code` | form | `string` | True | ID товара |
| `goods[].quantity` | form | `float` | True | Количество |
| `goods[].price` | form | `float` | True | Цена |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `confirm_mpc`

`POST /v2/cards/{card_id}/confirmMPC`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `contract_id` | header | `string` | True | ID договора |
| `code` | form | `string` | True | Код из СМС |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `create_invite`

`POST /v2/invites`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `role` | json | `json` | True | ID роли |
| `mobile` | json | `string` | False | Номер телефона. Обязательный, если не заполнено поле email. |
| `email` | json | `string` | False | Email. Обязательный, если не заполнено поле mobile. |
| `cards` | json | `json` | False | Массив карт, к которым будет привязан пользователь после регистрации. [“4233424”,”4324234”] |
| `contracts` | json | `json` | False | Массив договоров, к которым будет привязан пользователь после регистрации. [{“id”:”1-FFFFF”,”template_id”:”1-KKKK”},{“id”:”1-RRRRR”,”template_id”:null}] |
| `contracts[].id` | json | `string` | True | ID договора |
| `contracts[].template_id` | json | `string` | False | ID шаблона виртуальной карты |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.id` | `string` | True | ID приглашения |
| `data.url` | `string` | True | Уникальная ссылка для регистрации |
| `data.attempts` | `uint` | True | Количество попыток повторных отправок в день |
| `data.expired_at` | `timestamp` | True | Дата окончания |

`POST /v2/invites_free`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `role` | json | `json` | True | ID роли |
| `mobile` | json | `string` | False | Номер телефона. Обязательный, если не заполнено поле email. |
| `email` | json | `string` | False | Email. Обязательный, если не заполнено поле mobile. |
| `cards` | json | `json` | False | Массив карт, к которым будет привязан пользователь после регистрации. [“4233424”,”4324234”] |
| `contracts` | json | `json` | False | Массив договоров, к которым будет привязан пользователь после регистрации. [{“id”:”1-FFFFF”,”template_id”:”1-KKKK”},{“id”:”1-RRRRR”,”template_id”:null}] |
| `contracts[].id` | json | `string` | True | ID договора |
| `contracts[].template_id` | json | `string` | False | ID шаблона виртуальной карты |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.id` | `string` | True | ID приглашения |
| `data.url` | `string` | True | Уникальная ссылка для регистрации |
| `data.attempts` | `uint` | True | Количество попыток повторных отправок в день |
| `data.expired_at` | `timestamp` | True | Дата окончания |

## `create_template`

`POST /v2/vc/templates`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `name` | form | `string` | True | Имя шаблона ВК (Уникальное в рамках договора) |
| `type` | form | `string` | True | Тип карты (Limit – лимитная схема, Wallet – электронный кошелек) |
| `contract_id` | form | `string` | True | ID договора |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID шаблона |

## `create_template_georestriction`

`POST /v2/vc/templates/{template_id}/georestrictions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | json | `string` | True | ID договора |
| `country` | json | `string` | True | ID страны |
| `region` | json | `string` | False | ID региона |
| `partner` | json | `string` | False | ID партнера |
| `service_center` | json | `string` | False | ID АЗС |
| `restriction_type` | json | `uint` | True | 1 – Разрешающий геоограничитель, 2 – Запрещающий геоограничитель |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID геоограничителя |

## `create_template_limit`

`POST /v2/vc/templates/{template_id}/limits`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | json | `string` | True | ID договора |
| `amount` | json | `json` | conditional | Ограничение по количеству (Обязательный параметр, если не заполнено sum) |
| `sum` | json | `json` | conditional | Ограничение по сумме (Обязательный параметр, если не заполнено amount) |
| `time` | json | `json` | True | Длительность, период времени |
| `term` | json | `json` | False | Ограничение лимита по дням недели и времени |
| `product_type` | json | `string` | True | ID типа продукта |
| `product_group` | json | `string` | False | ID группы продукта |
| `create_restriction` | json | `bool` | False | Требуется ли создать ограничитель (true/false) |
| `amount.unit` | json | `string` | True | Единица измерения |
| `amount.value` | json | `float` | True | Суммарное количество ограничения |
| `sum.currency` | json | `string` | True | Валюта |
| `sum.value` | json | `float` | True | Суммарный размер ограничения |
| `time.number` | json | `uint` | True | Значение |
| `time.type` | json | `uint` | True | Период действия ограничения: 2 – Разовый, 3 – Сутки, 4 – Неделя, 5 – Месяц, 6 – Квартал, 7 – Год |
| `term.days` | json | `string[7]` | False | Строка из 7 нулей и единиц. 1 – ограничение применяется в этот день, 0 – нет |
| `term.time` | json | `json` | False | Время обслуживания |
| `term.type` | json | `uint` | True | Способ применения ограничения. 1 - Ограничение применяется всегда (во все указанные дни недели) 2 - Ограничение применяется только в рабочие дни 3 - Ограничение применяется только в выходные и праздничные дни |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID лимита |

## `create_template_restriction`

`POST /v2/vc/templates/{template_id}/restrictions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | json | `string` | True | ID договора |
| `product_type` | json | `string` | True | ID типа продукта |
| `product_group` | json | `string` | False | ID группы продукта |
| `restriction_type` | json | `uint` | True | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID ограничителя |

## `create_user`

`POST /v2/users`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `uuid` | form | `string` | True | Ваш внутренний ID водителя |
| `mobile` | form | `string` | True | Телефон водителя (Логин) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID нового водителя |

## `create_virtual_card`

`POST /v2/cards`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | form | `string` | False | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `template_id` | form | `string` | False | ID шаблона ВК (Не обязателен, если шаблон ВК был ранее закреплен за пользователем) |
| `user_id` | form | `string` | False | ID пользователя (Если указан, то выпуск карты производится с использванием данных указанного клиента пользователя) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.id` | `string` | True | ID карты |
| `data.number` | `string` | False | Номер карты |
| `data.carrier` | `string` | False | Тип карты |
| `data.product` | `string` | False | Тип продукта карты |
| `data.status` | `string` | False | Статус карты |

## `delete_invite`

`DELETE /v2/invites/{invite_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `delete_mpc`

`POST /v2/cards/{card_id}/deleteMPC`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `contract_id` | header | `string` | True | ID договора |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `delete_template`

`DELETE /v2/vc/templates/{template_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `delete_template_georestriction`

`DELETE /v2/vc/templates/{template_id}/georestrictions/{georestriction_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `delete_template_limit`

`DELETE /v2/vc/templates/{template_id}/limits/{limit_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `delete_template_restriction`

`DELETE /v2/vc/templates/{template_id}/restrictions/{restriction_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `delete_user`

`DELETE /v2/users/{user_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `detach_card`

`POST /v2/users/{user_id}/detachCard`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | form | `string` | True | ID карты |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `detach_contracts`

`POST /v2/users/{user_id}/detachContracts`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `data` | json | `[string, string]` | False | ID договоров |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `download_report_file`

`GET /v2/reports/jobs/{job_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `job_id` | path | `string` | True | Job_ID отчета |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.Содержимое файла` | `Поток` | False | Требуется сформировать файл из потока данных |

## `download_report_file_v1`

`GET /v1/getReportFile`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `job_id` | query | `string` | True | Job_ID отчета |
| `archive` | query | `bool` | False | Архивирование отчета в ZIP формат |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.Содержимое файла` | `Поток` | False | Требуется сформировать файл из потока данных |

## `generate_payment_qr`

`POST /v2/cards/{card_id}/pay`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `pin` | form | `string` | True | Пин-код МПК |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.code` | `string` | True | Платежная строка |
| `data.end_date` | `uint` | True | Срок жизни платежной строки |
| `data.transaction_count` | `uint` | True | Количество проведенных транзакций |
| `data.tries` | `uint` | True | Максимальное количество попыток оплаты по МПК |

## `get_azs_filters`

`GET /v2/azs/filters`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data[].filter` | `string` | True | Код группы фильтра |
| `data[].name` | `string` | True | Название группы фильтра |
| `data[].items` | `array` | True | Массив элементов группы фильтра |
| `data[].items[].code` | `string` | True | Код элемента фильтра (значение для фильтрации) |
| `data[].items[].name` | `string` | True | Название элемента фильтра (для отображения пользователю) |

## `get_azs_list_v1`

`GET /v1/AZS`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `page` | query | `uint` | False | Номер страницы начиная с 1 |
| `onpage` | query | `uint` | False | Количество элементов на странице (0 – если нужно вывести все элементы) |
| `filter` | query | `json` | False | JSON объект для фильтрации списка |
| `q` | query | `string` | False | Поисковая строка запроса (Ищет по наименованию ТТ, адресу и номеру терминала) |
| `id` | query | `string` | False | ID торговой точки (для детального показа 1й ТТ) |
| `filter.region` | query | `[string, string]` | False | Массив регионов (справочник Region) |
| `filter.country` | query | `[string, string]` | False | Массив стран (справочник Country) |
| `filter.owntype` | query | `[string, string]` | False | Массив типов собственности (справочник OwnType) |
| `filter.type` | query | `[string, string]` | False | Массив типов принадлежности (справочник POIType) |
| `filter.status` | query | `[string, string]` | False | Массив статусов (257 - ТТ работает, 258 - ТТ не работает) |
| `filter.services` | query | `[uint,uint]` | False | Массив предоставляемых услуг на ТТ (справочник Services) |
| `filter.goods` | query | `[string, string]` | False | Массив имеющейся в продаже номенклатуры (справочник GoodsCode) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID торговой точки |
| `data.result[].siebelId` | `string` | True | ID торговой точки (для отчета) |
| `data.result[].contractNumber` | `string` | True | Код ТТ |
| `data.result[].contractName` | `string` | True | Название торговой точки |
| `data.result[].status` | `string` | True | Статус торговой точки, 257 – работает, 258 – не работает |
| `data.result[].countryCode` | `string` | True | Код страны |
| `data.result[].regionCode` | `string` | True | Код региона |
| `data.result[].secessionGPN` | `string` | False | Тип по местоположению |
| `data.result[].belongsTo` | `string` | True | Название |
| `data.result[].partner` | `string` | True | ID партнера |
| `data.result[].ownType` | `string` | True | Тип собственности по отношению к ГПН |
| `data.result[].locationType` | `string` | False | Расположение |
| `data.result[].brand` | `string` | False | Бренд |
| `data.result[].openDate` | `string` | True | Дата открытия |
| `data.result[].closeDate` | `string` | False | Дата закрытия тип торговой точки |
| `data.result[].latitude` | `string` | True | Координаты – широта |
| `data.result[].longitude` | `string` | True | Координаты – долгота |
| `data.result[].type` | `string` | True | Тип торговой точки |
| `data.result[].timeZone` | `string` | False | Часовой пояс |
| `data.result[].services` | `[uint,uint]` | False | Массив с ID услугами. Описание услуг можно посмотреть в справочнике Services. |
| `data.result[].terminals` | `json` | False | Терминалы ТТ |
| `data.result[].address` | `json` | True | Адрес АЗС |
| `data.result[].searchTxt` | `string` | True | Строка для запроса поиска |
| `data.result[].phone` | `string` | False | Телефон |
| `data.result[].height_post` | `string` | False | Высота поста (в метрах) |
| `data.result[].working_time` | `array` | False | Рабочее время |
| `data.result[].prices` | `json` | False | Цены товаров на торговой точке |
| `data.result[].only_virtual_card` | `bool` | False | Только ли виртуальные карты принимаются |
| `data.result[].accept_cards` | `bool` | False | Принимаются ли карты |
| `data.result[].hidden_on_map` | `bool` | False | Скрыта ли на карте |
| `data.result[].active` | `bool` | False | Активна ли ТО |
| `data.result[].POIType` | `string` | False | Код типа ТО |
| `data.result[].Terminals[].id` | `string` | True | Идентификатор терминала |
| `data.result[].Terminals[].active` | `bool` | True | Статус терминала (true – включен, false – выключен) |
| `data.result[].Terminals[].name` | `string` | True | Наименование терминала |
| `data.result[].Terminals[].status` | `string` | True | Статус терминала |
| `data.result[].Terminals[].type` | `string` | True | Тип терминала |
| `data.result[].Terminals[].connectionType` | `string` | True | Способ подключения |
| `data.result[].Terminals[].number` | `string` | True | Номер терминала |
| `data.result[].Address.track_id` | `string` | False | Номер трассы |
| `data.result[].Address.kmRoad` | `string` | False | Километр |
| `data.result[].Address.roadSide` | `string` | False | Сторона дороги |
| `data.result[].Address.city` | `string` | True | Город |
| `data.result[].Address.street` | `string` | False | Улица |
| `data.result[].Address.house` | `string` | False | Дом |
| `data.result[].Address.building` | `string` | False | Строение |
| `data.result[].Address.phone` | `string` | False | Телефон |
| `data.result[].Address.fax` | `string` | False | Факс |
| `data.result[].Prices[].ID` | `string` | True | ID цены |
| `data.result[].Prices[].GasStationID` | `string` | True | ID торговой точки |
| `data.result[].Prices[].GoodsCode` | `string` | True | Товары, описание товаров можно посмотреть в справочнике GoodsCode |
| `data.result[].Prices[].Price` | `string` | True | Цена |
| `data.result[].Prices[].Currency` | `string` | True | Валюта |
| `data.result[].Prices[].DateTo` | `string` | True | Дата действия цены |
| `data.result[].Prices[].DateFrom` | `string` | True | Дата обновления цены |
| `data.result[].working_time[].Weekday` | `string` | True | День недели или режим работы (Monday + Round-The-Clock - круглосуточно, Everyday - каждый день) |
| `data.result[].working_time[].StartWorkTime` | `string` | False | Время открытия |
| `data.result[].working_time[].FinishWorkTime` | `string` | False | Время закрытия |

## `get_azs_list_v2`

`GET /v2/azs`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `q` | query | `string` | False | Поисковая строка запроса (Ищет по наименованию АЗС и адресу) |
| `id` | query | `string` | False | ID точки АЗС |
| `page` | query | `int` | False | Номер страницы |
| `on_page` | query | `int` | False | Количество записей на странице |
| `filter` | query | `json` | False | JSON объект для фильтрации списка |
| `filter.services_with_card` | query | `array` | False | Массив кодов услуг по топливной карте |
| `filter.services_without_card` | query | `array` | False | Массив кодов услуг для водителей |
| `filter.own_types` | query | `array` | False | Массив кодов типов владения |
| `filter.payment_types` | query | `array` | False | Массивкодов способов оплаты |
| `filter.fuel` | query | `array` | False | Массив кодов бензинов |
| `filter.diesel` | query | `array` | False | Массив кодов дизельных топлив |
| `filter.gaz` | query | `array` | False | Массив кодов газа |
| `filter.electric_charging_station` | query | `array` | False | Массив кодов электрозаправка |
| `filter.adblue` | query | `array` | False | Массив кодов AdBlue |
| `filter.poi_types` | query | `array` | False | Массив кодов типов азс |
| `filter.countries` | query | `array` | False | Массив кодов стран |
| `filter.regions` | query | `array` | False | Массив кодов регионов |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `int` | True | Кол-во актов |
| `data.result` | `array` | True | Массив объектов Poi |
| `data.result[].id` | `int` | True | ID торговой точки |
| `data.result[].siebel_id` | `int` | True | ID торговой точки в CRM |
| `data.result[].status` | `string` | True | Статус |
| `data.result[].full_name` | `string` | False | Полное название |
| `data.result[].brand` | `string` | False | Бренд |
| `data.result[].poi_type_name` | `string` | False | Именование типа |
| `data.result[].poi_type_code` | `string` | False | Код типа |
| `data.result[].own_type_name` | `string` | True | Название типа собственности |
| `data.result[].own_type_code` | `string` | True | Код типа собственности (по отношению к ГПН) |
| `data.result[].contract_name` | `string` | False | Название договора |
| `data.result[].contract_number` | `string` | False | Номер договора |
| `data.result[].phone` | `string` | False | Телефон |
| `data.result[].utc_timezone` | `string` | True | UTC часовой пояс АЗС ("+5") |
| `data.result[].time_zone` | `string` | False | Часовой пояс АЗС относительно Москвы |
| `data.result[].open_date` | `string` | False | Дата открытия |
| `data.result[].close_date` | `string` | False | Дата закрытия |
| `data.result[].last_update` | `string` | False | Дата последнего обновления |
| `data.result[].height_post` | `string` | False | Высота поста |
| `data.result[].country_name` | `string` | True | Название страны |
| `data.result[].country_code` | `string` | True | Код страны |
| `data.result[].region_name` | `string` | False | Название региона |
| `data.result[].region_code` | `string` | False | Код региона |
| `data.result[].address_full` | `string` | False | Полный адрес |
| `data.result[].location` | `object` | False | Локация |
| `data.result[].latitude` | `string` | False | Координаты – широта |
| `data.result[].longitude` | `string` | False | Координаты – долгота |
| `data.result[].location_type` | `string` | False | Тип локации |
| `data.result[].adblue` | `object` | False | Услуги AdBlue |
| `data.result[].electric_charging_station` | `object` | False | Электрозарядка |
| `data.result[].secession_gpn` | `string` | False | Отделение ГПН |
| `data.result[].partner` | `string` | False | Идентификатор партнера |
| `data.result[].belongs_to` | `string` | False | Принадлежность |
| `data.result[].info` | `string` | False | Дополнительная информация |
| `data.result[].search_txt` | `string` | True | Строка для запроса поиска |
| `data.result[].accept_cards` | `bool` | True | Принимаются ли банковские карты |
| `data.result[].services_with_card` | `object` | False | Список услуг по ТК |
| `data.result[].services_without_card` | `object` | False | Список услуг без ТК |
| `data.result[].prices` | `array` | False | Список товаров с указанием цен |
| `data.result[].payment_type` | `array` | False | Доступные способы оплаты |
| `data.result[].terminals` | `array` | False | Терминалы |
| `data.result[].address` | `object` | False | Адрес |
| `data.result[].working_time` | `array` | False | Время работы |
| `data.result[].location.type` | `string` | False | Тип геоданных (Point - точка) |
| `data.result[].location.coordinates` | `array[float]` | False | Массив из двух элементов: долгота и широта АЗС |
| `data.result[].payment_type[].code` | `string` | False | Код способа оплаты |
| `data.result[].payment_type[].name` | `string` | False | Название способа оплаты |
| `data.result[].terminals[].id` | `string` | False | Идентификатор терминала |
| `data.result[].terminals[].active` | `bool` | False | Статус терминала (true – включен, false – выключен) |
| `data.result[].terminals[].name` | `string` | False | Наименование терминала |
| `data.result[].terminals[].status` | `string` | False | Статус терминала |
| `data.result[].terminals[].type` | `string` | False | Тип терминала |
| `data.result[].terminals[].connectionType` | `string` | False | Способ подключения |
| `data.result[].terminals[].number` | `string` | False | Номер терминала |
| `data.result[].address.track_id` | `string` | False | Номер трассы |
| `data.result[].address.kmRoad` | `string` | False | Километр |
| `data.result[].address.roadSide` | `string` | False | Сторона дороги |
| `data.result[].address.city` | `string` | False | Город |
| `data.result[].address.street` | `string` | False | Улица |
| `data.result[].address.house` | `string` | False | Дом |
| `data.result[].address.building` | `string` | False | Строение |
| `data.result[].address.phone` | `string` | False | Телефон |
| `data.result[].address.fax` | `string` | False | Факс |
| `data.result[].prices[].ID` | `string` | False | ID цены |
| `data.result[].prices[].GasStationID` | `string` | False | ID торговой точки |
| `data.result[].prices[].GoodsCode` | `string` | False | Товары, описание товаров можно посмотреть в справочнике GoodsCode |
| `data.result[].prices[].Price` | `string` | False | Цена |
| `data.result[].prices[].Currency` | `string` | False | Валюта |
| `data.result[].prices[].DateTo` | `string` | False | Дата действия цены |
| `data.result[].prices[].DateFrom` | `string` | False | Дата обновления цены |
| `data.result[].prices[].hex_color` | `string` | False | Код цвета цены |
| `data.result[].prices[].name` | `string` | False | Название товара |
| `data.result[].prices[].CurrencyName` | `string` | False | Название валюты |
| `data.result[].prices[].sort` | `int` | False | Порядок сортировки |
| `data.result[].working_time[].Weekday` | `string` | False | День недели или режим работы |
| `data.result[].working_time[].StartWorkTime` | `string` | False | Время открытия |
| `data.result[].working_time[].FinishWorkTime` | `string` | False | Время закрытия |
| `data.result[].working_time[].Everyday` | `bool` | True | Признак, что точка работает ежедневно |
| `data.result[].working_time[].Round-The-Clock` | `bool` | True | Признак, что точка работает круглосуточно |
| `data.result[].services_with_card.name` | `string` | True | Название группы |
| `data.result[].services_with_card.items` | `array` | True | Массив объектов, представляющих отдельные сервисы в группе |
| `data.result[].services_without_card.name` | `string` | True | Название группы |
| `data.result[].services_without_card.items` | `array` | True | Массив объектов, представляющих отдельные сервисы в группе |
| `data.result[].adblue.name` | `string` | True | Название группы |
| `data.result[].adblue.items` | `array` | True | Массив объектов, представляющих отдельные сервисы в группе |
| `data.result[].electric_charging_station.name` | `string` | True | Название группы |
| `data.result[].electric_charging_station.items` | `array` | True | Массив объектов, представляющих отдельные сервисы в группе |
| `data.result[].services_with_card.items[].name` | `string` | True | Название сервиса |
| `data.result[].services_with_card.items[].code` | `int` | True | Код сервиса |
| `data.result[].services_with_card.items[].sort` | `int` | False | Порядок сортировки |
| `data.result[].services_without_card.items[].name` | `string` | True | Название сервиса |
| `data.result[].services_without_card.items[].code` | `int` | True | Код сервиса |
| `data.result[].services_without_card.items[].sort` | `int` | False | Порядок сортировки |
| `data.result[].adblue.items[].name` | `string` | True | Название сервиса |
| `data.result[].adblue.items[].code` | `int` | True | Код сервиса |
| `data.result[].adblue.items[].sort` | `int` | False | Порядок сортировки |
| `data.result[].electric_charging_station.items[].name` | `string` | True | Название сервиса |
| `data.result[].electric_charging_station.items[].code` | `int` | True | Код сервиса |
| `data.result[].electric_charging_station.items[].sort` | `int` | False | Порядок сортировки |

## `get_card_detail`

`GET /v1/cards`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта |
| `card_id` | query | `string` | True | ID карты |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID карты |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].number` | `string` | True | Номер карты |
| `data.result[].status` | `string` | True | ID статуса карты |
| `data.result[].can_work_offline` | `bool` | True | Возможность обслуживания карты в режиме оффлайн |
| `data.result[].card_auth_type` | `string` | True | Наименование способа авторизации карты |
| `data.result[].comment` | `string` | False | Комментарий карты |
| `data.result[].date_last_usage` | `string` | False | Дата последнего использования |
| `data.result[].date_released` | `string` | False | Дата выпуска карты |
| `data.result[].servicecenter_last_usage` | `string` | False | ID ТО последнего обслуживания |
| `data.result[].transaction_timeout` | `json` | False | Минимальное время между транзакциями |
| `data.result[].product` | `string` | True | Тип продукта (Лимитная карта или Электронный кошелек) |
| `data.result[].carrier` | `string` | True | Тип карты (Plastic – физическая карта, Virtual Card – виртуальная карта) |
| `data.result[].available` | `string` | True | Баланс электронного кошелька |
| `data.result[].currency` | `string` | True | Валюта карты |
| `data.result[].payment_of_tolls` | `string` | True | Возможность оплаты дорожных сборов |
| `data.result[].mpc` | `bool` | True | Флаг выпуска МПК по карте (Существует ли МПК на карте) |
| `data.result[].pin_reset` | `uint` | True | Количество доступных попыток сброса неверных попыток ввода PIN – кода по карте (verifyPIN) |
| `data.result[].pin_counter` | `uint` | True | Количество доступных попыток ввода PIN – кода по карте (при значении 0 по карте нельзя обслужиться) |
| `data.result[].previous` | `string` | False | Предыдущая карта |
| `data.result[].next` | `string` | False | Следующая карта |
| `data.result[].transaction_timeout.type` | `uint` | True | Единицы изменения |
| `data.result[].transaction_timeout.value` | `uint` | True | Значение ограничения |

## `get_card_drivers`

`GET /v2/cards/{card_id}/drivers`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID пользователя |
| `data.result[].login` | `string` | True | Логин пользователя |
| `data.result[].first_name` | `string` | True | Имя |
| `data.result[].last_name` | `string` | True | Фамилия |
| `data.result[].middle_name` | `string` | False | Отчество |
| `data.result[].date` | `string` | False | Дата рождения |
| `data.result[].position` | `string` | False | Должность |
| `data.result[].role` | `json` | True | Роль пользователя |
| `data.result[].mobile_phone` | `string` | True | Телефон |
| `data.result[].email` | `string` | False | Email |

## `get_card_groups`

`GET /v1/cardGroups`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID договора |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID группы карт |
| `data.result[].name` | `string` | True | Название группы |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].cards_count` | `string` | True | Количество карт в этой группе |
| `data.result[].status` | `string` | True | Статус группы |

## `get_card_transactions_v2`

`GET /v2/cards/{card_id}/transactions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `date_from` | query | `string` | True | Начало периода транзакций |
| `date_to` | query | `string` | True | Окончание периода транзакций |
| `page_limit` | query | `uint` | False | Количество транзакций на странице. 500, если не указано. |
| `page_offset` | query | `uint` | False | Количество транзакций, которые пропускаются |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID транзакции |
| `data.result[].timestamp` | `string` | True | Дата и время транзакции по местному времени |
| `data.result[].utc_time` | `string` | True | Дата и время транзакции по UTC |
| `data.result[].card_id` | `string` | True | ID карты |
| `data.result[].poi_id` | `string` | True | ID точки обслуживания |
| `data.result[].terminal_id` | `string` | True | ID терминала |
| `data.result[].type` | `string` | True | ID типа транзакции |
| `data.result[].product_id` | `string` | True | ID продукта |
| `data.result[].product_name` | `string` | True | Наименование товара |
| `data.result[].product_category_id` | `string` | True | ID категории продукта |
| `data.result[].currency` | `string` | True | ID валюты |
| `data.result[].check_id` | `string` | True | ID чека |
| `data.result[].stor_transaction_id` | `string` | True | ID прямой транзакции |
| `data.result[].is_storno` | `bool` | True | Признак сторнирования |
| `data.result[].is_manual_correction` | `bool` | True | Признак ручной корректировки |
| `data.result[].qty` | `uint` | True | Количество единиц товара |
| `data.result[].price` | `string` | True | Цена со скидкой клиента |
| `data.result[].price_no_discount` | `string` | True | Цена без скидки |
| `data.result[].sum` | `string` | True | Сумма со скидкой клиента |
| `data.result[].sum_no_discount` | `string` | True | Сумма без скидки |
| `data.result[].discount` | `string` | True | Сумма скидки |
| `data.result[].exchange_rate` | `string` | True | Курс пересчёта |
| `data.result[].card_number` | `string` | True | Номер карты |
| `data.result[].payment_type` | `string` | True | Тип платежа |

## `get_cards_by_group`

`GET /v1/cards`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта |
| `group_id` | query | `string` | True | ID группы карт |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID карты |
| `data.result[].group` | `string` | False | ID группы карт, к которой принадлежит карта |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].number` | `string` | True | Номер карты |
| `data.result[].status` | `string` | True | ID статуса карты |
| `data.result[].comment` | `string` | False | Комментарий карты |
| `data.result[].product` | `string` | True | Тип продукта (Лимитная карта или Электронный кошелек) |
| `data.result[].payment_of_tolls` | `string` | True | Возможность оплаты дорожных сборов |
| `data.result[].sync_group_state` | `string` | False | Статус синхронизации группы карт |

## `get_cards_v1`

`GET /v1/cards`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта |
| `cache` | query | `bool` | False | Кеш карт. false или не задан - данные берутся по прямому запросу из процессинга. |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID карты |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].number` | `string` | True | Номер карты |
| `data.result[].status` | `string` | True | ID статуса карты |
| `data.result[].can_work_offline` | `bool` | True | Возможность обслуживания карты в режиме оффлайн |
| `data.result[].card_auth_type` | `string` | True | Наименование способа авторизации карты |
| `data.result[].comment` | `string` | False | Комментарий карты |
| `data.result[].date_expired` | `string` | True | Дата окончания срока действия |
| `data.result[].date_last_usage` | `string` | False | Дата последнего использования |
| `data.result[].date_released` | `string` | False | Дата выпуска карты |
| `data.result[].servicecenter_last_usage` | `string` | False | ID ТО последнего обслуживания |
| `data.result[].transaction_last_detail` | `string` | False | Детали последней транзакции |
| `data.result[].transaction_timeout` | `json` | False | Минимальное время между транзакциями |
| `data.result[].product` | `string` | True | Тип продукта (Лимитная карта или Электронный кошелек) |
| `data.result[].payment_of_tolls` | `string` | True | Возможность оплаты дорожных сборов |
| `data.result[].transaction_timeout.type` | `uint` | True | Единицы изменения |
| `data.result[].transaction_timeout.value` | `uint` | True | Значение ограничения |

## `get_cards_v2`

`GET /v2/cards`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | False | ID договора (Можно передать в заголовке запроса, а не только в URI - строке). Если не передать, то подставим 1й договор из списка. |
| `group_id` | query | `string` | False | ID группы карт. При передаче параметра отобразит только карты этой группы. |
| `sort` | query | `string` | False | Сортировка (sort=-id). Поле для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC). |
| `q` | query | `string` | False | Поисковый запрос (Ищет по комментарию на карте, по номерам карт). |
| `status` | query | `string` | False | Фильтрует по статусам карт (Справочник CardStatus) |
| `carrier` | query | `string` | False | Фильтрует по типу карты (Plastic – физическая карта, Virtual Card – виртуальная карта). |
| `platon` | query | `bool` | False | Отобразит карты с подключенной услугой Платон. |
| `avtodor` | query | `bool` | False | Отобразит карты с подключенной услугой Автодор. |
| `users` | query | `bool` | False | С помощью данного параметра подгружаются пользователи и в списке карт заполняются поля users и mpc. Время ответа зависит от количества карт и количества пользователей. |
| `page` | query | `string` | False | Номер страницы (Пагинация). |
| `onpage` | query | `string` | False | Элементов на странице (Пагинация). |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID карты |
| `data.result[].group_id` | `string` | False | ID группы карт, к которой принадлежит карта |
| `data.result[].group_name` | `string` | False | Название группы карт, к которой принадлежит карта |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].contract_name` | `string` | True | Наименование договора |
| `data.result[].number` | `string` | True | Номер карты |
| `data.result[].status` | `string` | True | ID статуса карты |
| `data.result[].status_name` | `string` | False | Название статуса карты |
| `data.result[].comment` | `string` | False | Комментарий карты |
| `data.result[].product` | `string` | True | ID типа продукта |
| `data.result[].product_name` | `string` | False | Название типа продукта |
| `data.result[].carrier` | `string` | True | Тип карты |
| `data.result[].carrier_name` | `string` | False | Название типа карты |
| `data.result[].platon` | `bool` | True | Возможность использования услуги Платон |
| `data.result[].avtodor` | `bool` | True | Возможность использования услуги Автодор |
| `data.result[].sync_group_state` | `string` | False | Статус синхронизации группы карт |
| `data.result[].users` | `[string, string]` | False | Список ID пользователей к которым привязана карта |
| `data.result[].mpc` | `bool` | False | Существует ли МПК на карте |

## `get_contract_data`

`GET /v1/getPartContractData`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.mpc` | `bool` | True | Разрешен ли выпуск виртуальных карт |
| `data.template_id` | `string` | True | ID шаблона виртуальных карт |
| `data.status` | `string` | True | Статус Way4 |
| `data.status_crm` | `string` | True | Статус СРМ |
| `data.payment_term_id` | `string` | False | ID справочника условия оплаты |
| `data.payment_scheme_id` | `string` | False | ID cправочника схема оплаты |
| `data.Is_dealer` | `bool` | True | Признак дилерский |
| `data.balanceData` | `json` | True | Данные по расходу и балансу договора |
| `data.contractData` | `json` | True | Данные договора |
| `data.managerData` | `json` | True | Данные по менеджеру договора |
| `data.cardsData` | `json` | True | Данные по количеству карт и групп карт на договоре |
| `data.balanceData.available_amount` | `string` | True | Доступный остаток |
| `data.balanceData.own_balance` | `string` | True | Собственные средства |
| `data.balanceData.balance` | `string` | True | Собственные средства клиента с учетом блокировок |
| `data.balanceData.consumption_for_month` | `string` | True | Расход в текущем месяце (в валюте контракта) |
| `data.balanceData.consumption_for_month_volume` | `string` | True | Объем потребления в текущем месяце (в литрах) |
| `data.balanceData.consumption_for_prev_month_volume` | `string` | True | Объем потребления в предыдущем месяце (в литрах) |
| `data.balanceData.last_payment_sum` | `string` | False | Сумма последнего платежа |
| `data.balanceData.last_payment_date` | `string` | False | Дата последнего платежа |
| `data.balanceData.currency` | `string` | True | Валюта договора |
| `data.contractData.contract_id` | `string` | True | ID договора |
| `data.contractData.way_id` | `string` | True | ID договора в процессинге |
| `data.contractData.contract_number` | `string` | True | Номер договора |
| `data.contractData.unique_payment_id` | `string` | True | Уникальный идентификатор платежа (УИП) |
| `data.contractData.client` | `string` | True | ID клиента |
| `data.contractData.client_category` | `string` | True | Категория клиента |
| `data.contractData.contract_category` | `string` | True | Категория договора |
| `data.contractData.country` | `string` | True | Страна заключения |
| `data.contractData.region` | `string` | True | Регион заключения |
| `data.contractData.fin_institution` | `string` | True | Финансовый институт |
| `data.contractData.invoice_scheme` | `string` | True | Подключение инвойсирвоания |
| `data.contractData.invoice_period` | `string` | False | Дни выставления счетов |
| `data.contractData.invoice_pmt_delay` | `string` | False | Количество дней на оплату инвойса |
| `data.contractData.contract_status` | `string` | True | ID статуса договора |
| `data.contractData.contract_status_name` | `string` | True | Значение статуса договора |
| `data.contractData.pay_scheme` | `string` | True | Условия оплаты |
| `data.contractData.discount_scheme` | `string` | True | Схема расчета скидки (код из справочника DiscountScheme) |
| `data.contractData.auto_pay` | `string` | True | Признак разрешения для подключения автосписания с р/с |
| `data.contractData.auto_pay_type` | `string` | True | Тип подключения автоматического платежа |
| `data.contractData.credit_limit` | `string` | False | Кредитный лимит |
| `data.contractData.current_amount_limiter` | `string` | True | Накопленная сумма по контракту |
| `data.contractData.balance_amount_limiter` | `string` | False | Доступная сумма по контракту (max – current) |
| `data.contractData.max_amount_limiter` | `string` | False | Ограничение лимита на сумму договора |
| `data.contractData.date_open` | `string` | True | Дата заключения договора |
| `data.contractData.effective_date` | `string` | True | Дата вступления в силу |
| `data.contractData.end_date` | `string` | True | Дата окончания |
| `data.contractData.date_expire` | `string` | True | Дата закрытия |
| `data.contractData.product_type` | `bool` | True | Признак универсального топливного продукта (false – старый продукт, true - УТП) |
| `data.contractData.type_code` | `string` | True | Тип договора |
| `data.contractData.supplier_name` | `string` | True | Имя поставщика |
| `data.managerData.email` | `string` | True | Email менеджера по сопровождению |
| `data.managerData.first_name` | `string` | True | Имя менеджера по сопровождению |
| `data.managerData.last_name` | `string` | True | Фамилия менеджера по сопровождению |
| `data.managerData.middle_name` | `string` | False | Отчество менеджера по сопровождению |
| `data.managerData.work_phone` | `string` | False | Рабочий телефон менеджера по сопровождению |
| `data.cardsData.cards_quantity_all` | `string` | True | Число карт договора |
| `data.cardsData.cards_quantity_active` | `string` | True | Число активных карт договора |
| `data.cardsData.card_groups_quantity_all` | `string` | False | Число групп карт на договоре |

## `get_dictionary`

`GET /v1/getDictionary`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `name` | query | `string` | True | Наименование справочника: • CardStatus – Запрос списка статусов карт. • ContractStatus – Запрос списка статусов договора. • Country – Запрос списка стран. • Currency – Запрос списка валют. • Goods – Запрос списка топлива для цен на АЗС. • PaymentScheme – Запрос списка схем оплаты договора. • PaymentTerm – Запрос списка условий оплаты договора. • ProductGroup – Запрос списка групп продукта. • ProductType – Запрос списка типов продукта. • POIType – Запрос списка типов принадлежности АЗС. • Region – Запрос списка регионов. • Services – Запрос списка услуг на АЗС. • Unit – Запрос списка единиц измерения продуктов • Office – Запрос списка офисов продаж • POIPartner – Запрос списка партнеров • DiscountScheme – Запрос списка схем расчета скидки |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |

## `get_documents`

`GET /v2/documents`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `date_start` | query | `string` | True | Дата начала периода (Формат: 2019-01-01) |
| `date_end` | query | `string` | True | Дата окончания периода (Формат: 2020-01-01) |
| `page` | query | `string` | False | Номер страницы (Пагинация) |
| `on_page` | query | `string` | False | Элементов на странице (Пагинация) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID документа |
| `data.result[].name` | `string` | True | Наименование документа |
| `data.result[].name_doc` | `string` | False | Описание документа |
| `data.result[].number` | `string` | True | Номер документа |
| `data.result[].date` | `uint` | True | Дата формирования документа (timestamp) |
| `data.result[].total` | `float` | True | Сумма документа (включая НДС) |
| `data.result[].vat` | `float` | True | Сумма НДС |
| `data.result[].sum` | `float` | True | Сумма без НДС |
| `data.result[].currency` | `string` | True | Валюта |
| `data.result[].consignee` | `string` | False | Грузополучатель |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].contract_name` | `string` | True | Номер договора |

## `get_final_prices`

`POST /v2/cards/{card_id}/calculatePrices`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) |
| `poi_id` | form | `string` | True | ID точки обслуживания |
| `goods` | form | `array` | True | Массив идентикаторов продуктов |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.goods` | `json` | True | Массив данных |
| `data.goods[].code` | `string` | True | ID товара |
| `data.goods[].price` | `float` | True | Цена |

## `get_info`

`GET /v1/info`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `period` | query | `string` | False | Период формата за весь месяц (YYYY-MM 2018-10) или за конкретный день (YYYY-MM-DD 2018-10-10) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.from` | `string` | True | Начало периода |
| `data.to` | `string` | True | Конец периода |
| `data.client_info` | `json` | True | Информация об организации |
| `data.methods` | `json` | True | Статистика вызовов |
| `data.methods_info` | `json` | True | Описание методов |
| `data.client_info.Client` | `string` | True | ID организации |
| `data.client_info.ClientType` | `string` | True | Тип клиента (C – Клиент, D – Дилер, S – сабдилер) |
| `data.client_info.Contract` | `string` | False | ID договора |
| `data.client_info.ContractName` | `string` | False | Название договора |
| `data.client_info.PricePlan` | `string` | False | Тарифный план |
| `data.client_info.Cost` | `uint` | False | Стоимость тарифа |
| `data.client_info.Queries` | `uint` | False | Количество оплаченных запросов |
| `data.client_info.Additional` | `uint` | False | Количество доп. пакетов |
| `data.methods.all` | `uint` | True | Сумма всех вызовов |
| `data.methods_info.actions_bill` | `json` | True | Тарифицируемые методы |
| `data.methods_info.actions_not_bill` | `json` | True | Бесплатные методы |

## `get_invites`

`GET /v2/invites`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `role` | query | `string` | False | Фильтрация по ID роли (Supervisor, Regulatory, Driver, Readonly) |
| `status` | query | `string` | False | Фильтрация по статусу заявки (Active, Expired, Finished) |
| `user_id` | query | `string` | False | Отобразить инвайты по которым произошла регистрация пользователя (true) |
| `q` | query | `string` | False | Поисковый запрос (Ищет email и mobile) |
| `filter` | query | `json` | False | Объект фильтрации ({“status”:”Finished”,”role”:”Driver”}) |
| `sort` | query | `string` | False | Сортировка. Сортировка осуществляется формированием строки вида: sort=title,name,-date Поля для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC) |
| `page` | query | `string` | False | Номер страницы (Пагинация) |
| `on_page` | query | `string` | False | Элементов на странице (Пагинация) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID приглашения |
| `data.result[].user_id` | `string` | False | ID пользователя, который был создан с помощью этого инвайта. |
| `data.result[].url` | `string` | True | Уникальная ссылка для регистрации |
| `data.result[].status` | `string` | True | ID статуса приглашения |
| `data.result[].status_name` | `string` | True | Название статуса приглашения |
| `data.result[].role` | `string` | True | ID роли |
| `data.result[].role_name` | `string` | True | Название роли |
| `data.result[].attempts` | `uint` | True | Количество попыток повторных отправок в день |
| `data.result[].cards` | `json` | True | Список карт, которые будут привязаны к пользователю |
| `data.result[].initiator` | `string` | True | Логин инициатора приглашения |
| `data.result[].contracts` | `json` | True | Список договоров, которые будут привязаны к пользователю |
| `data.result[].mobile` | `string` | False | Мобильный телефон |
| `data.result[].email` | `string` | False | Email |
| `data.result[].communication_type` | `string` | True | Тип отправки (sms или email) |
| `data.result[].sended_at` | `timestamp` | False | Дата отправка |
| `data.result[].expired_at` | `timestamp` | True | Дата окончания |
| `data.result[].cards[].sid` | `string` | True | ID карты |
| `data.result[].cards[].number` | `string` | True | Номер карты |
| `data.result[].cards[].product` | `string` | True | Тип продукта (wallet или limit) |
| `data.result[].cards[].comment` | `string` | False | Комментарий на карте |
| `data.result[].cards[].status` | `string` | True | ID статуса карты |
| `data.result[].cards[].status_name` | `string` | True | Название статуса карты |
| `data.result[].cards[].contract_id` | `string` | True | ID договора |
| `data.result[].cards[].contract_name` | `string` | True | Номер договора |
| `data.result[].contracts[].sid` | `string` | True | ID договора |
| `data.result[].contracts[].number` | `string` | True | Номер договора |
| `data.result[].contracts[].status` | `string` | True | ID статуса договора |
| `data.result[].contracts[].status_name` | `string` | True | Название статуса договора |
| `data.result[].contracts[].template_id` | `string` | False | ID шаблона виртуальной карты |
| `data.result[].contracts[].cards_count` | `uint` | True | Количество карт на договоре |

## `get_invoices`

`GET /v2/invoices`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID инвойза |
| `data.result[].contract_id` | `string` | True | ID договора в процессинге |
| `data.result[].ref_number` | `string` | True | Номер инвойза |
| `data.result[].date_start` | `string` | True | Дата начала |
| `data.result[].date_end` | `uint` | True | Дата окончания |
| `data.result[].last_update` | `float` | True | Дата обновления |
| `data.result[].currency` | `float` | True | ID валюты (Справочник Currency) |
| `data.result[].amount` | `float` | True | Требуется оплатить |
| `data.result[].paid_amount` | `string` | True | Оплачено |
| `data.result[].status` | `string` | True | Статус инвойза |
| `data.result[].comment` | `string` | False | Комментарий к инвойзу |

## `get_limits`

`GET /v1/limit`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID договора |
| `card_id` | query | `string` | False | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все продуктовые лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех продуктовых лимитах по карте, даже если передан ID группы карт |
| `group_id` | query | `string` | False | ID группы карт. Если передан ID группы карты, то будут возвращены все продуктовые лимиты указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID лимита |
| `data.result[].card_id` | `string` | False | ID карты |
| `data.result[].group_id` | `string` | False | ID группы карт |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].productGroup` | `string` | False | ID группы продукта |
| `data.result[].productType` | `string` | True | ID типа продукта |
| `data.result[].amount` | `json` | False | Ограничение по количеству |
| `data.result[].sum` | `json` | False | Ограничение по сумме |
| `data.result[].term` | `json` | False | Ограничение по времени |
| `data.result[].time` | `json` | True | Длительность, период времени |
| `data.result[].transactions` | `json` | False | Ограничение по числу транзакций за период |
| `data.result[].date` | `string` | True | Дата последнего изменения |
| `data.result[].amount.unit` | `string` | True | Единица измерения |
| `data.result[].amount.value` | `float` | True | Суммарное количество ограничения |
| `data.result[].amount.used` | `float` | True | Использованное количество ограничения |
| `data.result[].sum.currency` | `string` | True | Валюта |
| `data.result[].sum.value` | `float` | True | Суммарный размер ограничения |
| `data.result[].sum.used` | `float` | True | Использованный объем ограничения |
| `data.result[].term.days` | `string[7]` | False | Строка из 7 нулей и единиц. 1 – ограничение применяется в этот день, 0 – нет |
| `data.result[].term.time` | `json` | False | Время обслуживания |
| `data.result[].term.type` | `uint` | True | Способ применения ограничения. 1 - Ограничение применяется всегда (во все указанные дни недели) 2 - Ограничение применяется только в рабочие дни 3 - Ограничение применяется только в выходные и праздничные дни |
| `data.result[].term.time.from` | `string` | True | От |
| `data.result[].term.time.to` | `string` | True | До |
| `data.result[].time.number` | `uint` | True | Значение. |
| `data.result[].time.type` | `uint` | True | Период действия ограничения. 2 – Разовый, 3 – Сутки, 4 – Неделя, 5 – Месяц, 6 – Квартал, 7 – Год |
| `data.result[].transactions.count` | `uint` | True | Количество транзакций по услуге |
| `data.result[].transactions.occured` | `uint` | True | Количество проведенных транзакций по ограничению |

## `get_mpc_qr_list`

`GET /v2/MPC`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | False | ID договора; если не указан, возвращаются все МПК клиента |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | True | Массив данных |
| `data.result[]._id` | `string` | True | ID записи |
| `data.result[].client_id` | `string` | True | ID клиента |
| `data.result[].user_id` | `string` | True | ID пользователя |
| `data.result[].login` | `string` | True | Логин пользователя |
| `data.result[].role` | `string` | True | ID роли пользователя |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].card_id` | `string` | True | ID топливной карты |
| `data.result[].card_number` | `string` | True | Номер топливной карты |
| `data.result[].device_id` | `string` | True | ID устройства |
| `data.result[].device_name` | `string` | True | Название устройства |
| `data.result[].tries` | `uint` | True | Максимальное количество попыток оплаты по МПК |
| `data.result[].transaction_count` | `uint` | True | Количество проведенных транзакций |
| `data.result[].use_mpc` | `bool` | True | Флаг работоспособности МПК |
| `data.result[].updated_at` | `string` | False | Время обновления записи |
| `data.result[].created_at` | `string` | True | Время создания записи |

## `get_payments`

`GET /v1/getPayments`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID платежа |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].date` | `string` | True | Дата платежа |
| `data.result[].amount` | `string` | True | Сумма платежа |
| `data.result[].currency` | `string` | True | Валюта |
| `data.result[].amount_client` | `string` | True | Сумма в валюте клиента |
| `data.result[].description` | `string` | True | Описание платежа |
| `data.result[].payment_name` | `string` | True | Название платежа |
| `data.result[].payment_type` | `string` | True | Тип платежа. P – Advice (Прямая); R – Reversal (Отмена); J – Adjustment (Частичная отмена) |
| `data.result[].payment_number` | `string` | True | Номер платежа |

## `get_region_limits`

`GET /v1/regionLimit`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта. |
| `card_id` | query | `string` | False | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все региональные лимиты, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех региональных лимитах по карте |
| `group_id` | query | `string` | False | ID группы карт. Если передан ID группы карты, то будут возвращены все региональные лимиты указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID регионального лимита |
| `data.result[].card_id` | `string` | False | ID карты |
| `data.result[].group_id` | `string` | False | ID группы карт |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].country` | `string` | True | Код страны обслуживания |
| `data.result[].region` | `string` | False | Код регион обслуживания |
| `data.result[].service_center` | `string` | False | ID АЗС |
| `data.result[].date` | `string` | True | Дата последнего изменения |
| `data.result[].limit_type` | `uint` | True | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |

## `get_report_job_list_v1`

`GET /v1/getReportJobList`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `json` | False | Массив данных |
| `data[].date` | `string` | True | Дата заказа отчета |
| `data[].client_id` | `string` | True | ID клиента |
| `data[].user_id` | `string` | True | ID логина |
| `data[].contract_id` | `string` | True | ID договора |
| `data[].job_id` | `string` | True | Job ID отчета |
| `data[].report_name` | `string` | True | Название отчета |
| `data[].report_format` | `string` | True | Формат отчета |

## `get_report_jobs`

`GET /v2/reports/jobs`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].date` | `string` | True | Дата заказа отчета |
| `data.result[].client_id` | `string` | True | ID клиента |
| `data.result[].user_id` | `string` | True | ID пользователя |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].job_id` | `string` | True | ID задания отчета |
| `data.result[].report_name` | `string` | True | Название отчета |
| `data.result[].report_format` | `string` | True | Формат отчета |
| `data.result[].available_after` | `uint` | True | Количество секунд через который будет доступен отчет |

## `get_reports`

`GET /v2/reports`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID отчета |
| `data.result[].name` | `string` | True | Название отчета |
| `data.result[].formats` | `[string,string]` | True | Доступные форматы |
| `data.result[].parameters` | `json` | True | Количество карт в этой группе |
| `data.result[].parameters[].name` | `string` | True | Наименование параметра |
| `data.result[].parameters[].value` | `string` | False | Значение |
| `data.result[].parameters[].label` | `string` | True | Отображаемое наименование параметра |
| `data.result[].parameters[].default_value` | `string` | False | Значение по умолчанию |
| `data.result[].parameters[].menu_values` | `json` | False | Список возможных значений |
| `data.result[].parameters[].type` | `string` | True | Тип параметра |

## `get_restrictions`

`GET /v1/restriction`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID контракта. |
| `card_id` | query | `string` | False | ID карты. Если ID карты и ID группы карт не переданы, то будут возвращены все товарные ограничители, привязанные к договору. Если передан ID карты, то будет возвращена информация о всех товарных ограничителях по карте, даже если передан ID группы карт |
| `group_id` | query | `string` | False | ID группы карт. Если передан ID группы карты, то будут возвращены все товарные ограничители указанной группы карт. Если передан ID карты и ID группы карт, то будет возвращена информация по карте |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID товарного ограничителя |
| `data.result[].card_id` | `string` | False | ID карты |
| `data.result[].group_id` | `string` | False | ID группы карт |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].productType` | `string` | False | ID типа продукта |
| `data.result[].productGroup` | `string` | False | ID группы продукта |
| `data.result[].productTypeName` | `string` | False | Название типа продукта |
| `data.result[].productGroupName` | `string` | False | Название группы продукта |
| `data.result[].date` | `string` | True | Дата последнего изменения |
| `data.result[].restriction_type` | `uint` | False | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель, 3 – Тип R |

## `get_template_georestrictions`

`GET /v2/vc/templates/{template_id}/georestrictions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID геоограничителя |
| `data.result[].template_id` | `string` | True | ID шаблона |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].date` | `string` | True | Дата создания |
| `data.result[].country` | `string` | True | ID страны |
| `data.result[].countryName` | `string` | True | Название страны |
| `data.result[].region` | `string` | False | ID региона |
| `data.result[].regionName` | `string` | False | Название региона |
| `data.result[].partner` | `string` | False | ID партнера |
| `data.result[].partnerName` | `string` | False | Название партнера |
| `data.result[].service_center` | `string` | False | ID АЗС |
| `data.result[].service_centerName` | `string` | False | Название АЗС |
| `data.result[].restriction_type` | `uint` | True | 1 – Разрешающий геоограничитель, 2 – Запрещающий геоограничитель |

## `get_template_limits`

`GET /v2/vc/templates/{template_id}/limits`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID лимита |
| `data.result[].template_id` | `string` | True | ID шаблона |
| `data.result[].date` | `string` | True | Дата создания |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].term` | `json` | True | Ограничение по времени |
| `data.result[].transactions` | `json` | True | Ограничение по числу транзакций за период |
| `data.result[].amount` | `json` | False | Ограничение по количеству |
| `data.result[].sum` | `json` | False | Ограничение по сумме |
| `data.result[].time` | `json` | True | Длительность, период времени |
| `data.result[].productType` | `string` | True | ID типа продукта |
| `data.result[].productGroup` | `string` | False | ID группы продукта |
| `data.result[].productTypeName` | `string` | True | Название типа продукта |
| `data.result[].productGroupName` | `string` | False | Название группы продукта |
| `data.result[].term.days` | `string[7]` | False | Строка из 7 нулей и единиц. 1 – ограничение применяется в этот день, 0 – нет |
| `data.result[].term.time` | `json` | False | Время обслуживания |
| `data.result[].term.type` | `uint` | True | Способ применения ограничения. 1 - Ограничение применяется всегда (во все указанные дни недели) 2 - Ограничение применяется только в рабочие дни 3 - Ограничение применяется только в выходные и праздничные дни |
| `data.result[].transactions.count` | `uint` | True | Количество транзакций по услуге |
| `data.result[].amount.unit` | `string` | True | Единица измерения |
| `data.result[].amount.value` | `float` | True | Суммарное количество ограничения |
| `data.result[].sum.currency` | `string` | True | Валюта |
| `data.result[].sum.value` | `float` | True | Суммарный размер ограничения |
| `data.result[].time.number` | `uint` | True | Значение |
| `data.result[].time.type` | `uint` | True | Период действия ограничения: 2 – Разовый, 3 – Сутки, 4 – Неделя, 5 – Месяц, 6 – Квартал, 7 – Год |

## `get_template_restrictions`

`GET /v2/vc/templates/{template_id}/restrictions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID ограничителя |
| `data.result[].template_id` | `string` | True | ID шаблона |
| `data.result[].date` | `string` | True | Дата создания |
| `data.result[].contract_id` | `string` | True | ID договора |
| `data.result[].productType` | `string` | True | ID типа продукта |
| `data.result[].productGroup` | `string` | False | ID группы продукта |
| `data.result[].productTypeName` | `string` | True | Название типа продукта |
| `data.result[].productGroupName` | `string` | False | Название группы продукта |
| `data.result[].restriction_type` | `uint` | True | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |

## `get_templates`

`GET /v2/vc/templates`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | False | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если не передать, то в ответе придут все шаблоны клиента. |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID шаблона |
| `data.result[].name` | `string` | True | Название шаблона (Уникальное в рамках договора) |
| `data.result[].type` | `string` | True | Тип карты (Limit – лимитная схема, Wallet – электронный кошелек) |
| `data.result[].contract_id` | `string` | True | ID договора |

## `get_transaction_detail`

`GET /v2/transactions/{transaction_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `transaction_id` | path | `uint` | True | ID транзакции |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID транзакции |
| `data.result[].date` | `string` | True | Дата транзакции |
| `data.result[].timestamp` | `string` | True | Дата и время транзакции по местному времени |
| `data.result[].utc_time` | `string` | True | Дата и время транзакции по UTC |
| `data.result[].card_id` | `string` | True | ID карты |
| `data.result[].poi_id` | `string` | True | ID точки обслуживания |
| `data.result[].terminal_id` | `string` | True | ID терминала |
| `data.result[].type` | `string` | True | ID типа транзакции |
| `data.result[].product_id` | `string` | True | ID продукта |
| `data.result[].product_name` | `string` | True | Наименование товара |
| `data.result[].product_category_id` | `string` | True | ID категории продукта |
| `data.result[].currency` | `string` | True | ID валюты |
| `data.result[].check_id` | `string` | True | ID чека |
| `data.result[].stor_transaction_id` | `string` | True | ID прямой транзакции |
| `data.result[].is_storno` | `bool` | True | Признак сторнирования |
| `data.result[].is_manual_correction` | `bool` | True | Признак ручной корректировки |
| `data.result[].qty` | `uint` | True | Количество единиц товара |
| `data.result[].price` | `string` | True | Цена со скидкой клиента |
| `data.result[].price_no_discount` | `string` | True | Цена без скидки |
| `data.result[].sum` | `string` | True | Сумма со скидкой клиента |
| `data.result[].sum_no_discount` | `string` | True | Сумма без скидки |
| `data.result[].discount` | `string` | True | Сумма скидки |
| `data.result[].exchange_rate` | `string` | True | Курс пересчёта |
| `data.result[].card_number` | `string` | True | Номер карты |
| `data.result[].payment_type` | `string` | True | Тип платежа |

## `get_transactions_v1`

`GET /v1/transactions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | query | `string` | True | ID договора |
| `card_id` | query | `string` | False | ID карты |
| `count` | query | `uint (1..30)` | False | Количество транзакций (если не указывать, то вернется 10 последних транзакций) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID транзакции |
| `data.result[].time` | `string` | True | Локальное время торговой точки |
| `data.result[].host_date` | `string` | True | Время проведения транзакции по процессингу в формате MSK +3 |
| `data.result[].currency` | `string` | True | ID валюты |
| `data.result[].card_id` | `string` | True | ID карты |
| `data.result[].service_center` | `string` | False | ID точки обслуживания |
| `data.result[].card_number` | `string` | True | Номер карты |
| `data.result[].base_cost` | `string` | True | Общая стоимость на ТО |
| `data.result[].cost` | `string` | True | Общая стоимость на ТО (в валюте договора клиента) |
| `data.result[].discount` | `string` | True | Общая cкидка (в валюте договора клиента) |
| `data.result[].discount_cost` | `string` | True | Общая cтоимость на ТО со скидкой (в валюте договора клиента) |
| `data.result[].incoming` | `bool` | True | Тип транзакции – входящая или исходящая. true - входящая транзакция, false – исходящая |
| `data.result[].request` | `json` | True | Тип транзакции |
| `data.result[].transaction_items` | `json` | False | Позиции чека транзакции по топливной карте |
| `data.result[].request.type` | `string` | True | Код типа транзакции |
| `data.result[].request.name` | `string` | True | Расшифровка типа транзакции |
| `data.result[].transaction_items[].id` | `string` | True | ID элемента транзакции |
| `data.result[].transaction_items[].rrn` | `string` | True | RRN – уникальный код операции |
| `data.result[].transaction_items[].product` | `string` | True | Продукт (название продукта) |
| `data.result[].transaction_items[].amount` | `string` | True | Количество |
| `data.result[].transaction_items[].price` | `string` | True | Цена на ТО |
| `data.result[].transaction_items[].base_cost` | `string` | True | Стоимость на ТО |
| `data.result[].transaction_items[].cost` | `string` | True | Стоимость на ТО (в валюте договора клиента) |
| `data.result[].transaction_items[].discount` | `string` | True | Скидка (в валюте договора клиента) |
| `data.result[].transaction_items[].discount_cost` | `string` | True | Стоимость на ТО со скидкой (в валюте договора клиента) |
| `data.result[].transaction_items[].transaction` | `string` | True | ID транзакции |
| `data.result[].transaction_items[].currency` | `string` | True | ID валюты |
| `data.result[].transaction_items[].unit` | `string` | True | ID eдиниц измерения продукта |

## `get_transactions_v2`

`GET /v2/transactions`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `date_from` | query | `string` | True | Начало периода транзакций |
| `date_to` | query | `string` | True | Окончание периода транзакций |
| `page_limit` | query | `uint` | False | Количество транзакций на странице. 500, если не указано. |
| `page_offset` | query | `uint` | False | Количество транзакций, которые пропускаются |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID транзакции |
| `data.result[].timestamp` | `string` | True | Дата и время транзакции по местному времени |
| `data.result[].utc_time` | `string` | True | Дата и время транзакции по UTC |
| `data.result[].card_id` | `string` | True | ID карты |
| `data.result[].poi_id` | `string` | True | ID точки обслуживания |
| `data.result[].terminal_id` | `string` | True | ID терминала |
| `data.result[].type` | `string` | True | ID типа транзакции |
| `data.result[].product_id` | `string` | True | ID продукта |
| `data.result[].product_name` | `string` | True | Наименование товара |
| `data.result[].product_category_id` | `string` | True | ID категории продукта |
| `data.result[].currency` | `string` | True | ID валюты |
| `data.result[].check_id` | `string` | True | ID чека |
| `data.result[].stor_transaction_id` | `string` | True | ID прямой транзакции |
| `data.result[].is_storno` | `bool` | True | Признак сторнирования |
| `data.result[].is_manual_correction` | `bool` | True | Признак ручной корректировки |
| `data.result[].qty` | `float` | True | Количество единиц товара |
| `data.result[].price` | `float` | True | Цена со скидкой клиента |
| `data.result[].price_no_discount` | `float` | True | Цена без скидки |
| `data.result[].sum` | `float` | True | Сумма со скидкой клиента |
| `data.result[].sum_no_discount` | `float` | True | Сумма без скидки |
| `data.result[].discount` | `float` | True | Сумма скидки |
| `data.result[].exchange_rate` | `float` | True | Курс пересчёта |
| `data.result[].card_number` | `string` | True | Номер карты |
| `data.result[].payment_type` | `string` | True | Тип платежа |

## `get_users`

`GET /v2/users`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `sort` | query | `string` | False | Сортировка. Сортировка осуществляется формированием строки вида: sort=title,name,-date Поля для сортировки указываются в виде строки, GET параметра sort, если перед наименованием поля поставить знак - , будет осуществляться сортировка по убыванию (DESC) |
| `filter` | query | `json` | False | Объект фильтрации ({"role":"Driver", "active":true}) |
| `q` | query | `string` | False | Поисковый запрос (Ищет по Фамилия, Имя, Отчество, Логин, Электронный ящик, Номер мобильного телефона) |
| `page` | query | `string` | False | Номер страницы (Пагинация) |
| `on_page` | query | `string` | False | Элементов на странице (Пагинация) |
| `contract_id` | query | `string` | False | Вывести пользователей с этим привязанным договором |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.total_count` | `uint` | True | Количество |
| `data.result` | `json` | False | Массив данных |
| `data.result[].id` | `string` | True | ID пользователя |
| `data.result[].login` | `string` | True | Логин пользователя |
| `data.result[].first_name` | `string` | True | Имя |
| `data.result[].last_name` | `string` | True | Фамилия |
| `data.result[].middle_name` | `string` | True | Отчество |
| `data.result[].date` | `string` | True | Дата рождения |
| `data.result[].position` | `string` | True | Должность |
| `data.result[].role` | `json` | True | Роль пользователя |
| `data.result[].active` | `bool` | False | Активность пользователя |
| `data.result[].access` | `json` | True | Доступ пользователя (ЛК, МП, API) |
| `data.result[].mobile_phone` | `string` | False | Телефон |
| `data.result[].email` | `string` | False | Email |
| `data.result[].contracts` | `json` | False | Список договоров к которым привязан пользователь |
| `data.result[].cards` | `json` | False | Список карт к которым привязан водитель (доступен только водителям, остальным пустой массив []) |
| `data.result[].role.id` | `string` | True | ID роли пользователя |
| `data.result[].role.name` | `string` | True | Название роли пользователя |
| `data.result[].access.web` | `bool` | True | Доступ в ЛК |
| `data.result[].access.api` | `bool` | True | Доступ в API |
| `data.result[].access.mobile` | `bool` | True | Доступ в МП |
| `data.result[].cards[].sid` | `string` | True | ID карты |
| `data.result[].cards[].number` | `string` | True | Номер карты |
| `data.result[].cards[].mpc` | `bool` | True | Выпущен ли мобильный профиль карты |
| `data.result[].cards[].product` | `string` | True | Тип продукта (wallet или limit) |
| `data.result[].cards[].comment` | `string` | False | Комментарий на карте |
| `data.result[].cards[].status` | `string` | True | ID статуса карты |
| `data.result[].cards[].contract_id` | `string` | True | ID договора |
| `data.result[].cards[].contract_name` | `string` | True | Номер договора |
| `data.result[].cards[].available` | `string` | True | Доступность пользователю |
| `data.result[].contracts[].sid` | `string` | True | ID договора |
| `data.result[].contracts[].number` | `string` | True | Номер договора |
| `data.result[].contracts[].available` | `string` | True | Доступность пользователю |
| `data.result[].contracts[].status` | `json` | True | Статус договора |
| `data.result[].contracts[].template_id` | `string` | False | ID шаблона виртуальной карты |
| `data.result[].contracts[].cards_count` | `uint` | True | Количество карт на договоре |
| `data.result[].contracts[].status.id` | `string` | True | ID статуса договора |
| `data.result[].contracts[].status.name` | `string` | True | Название статуса договора |

## `init_mpc`

`POST /v2/cards/{card_id}/initMPC`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `contract_id` | header | `string` | True | ID договора |
| `user_id` | form | `string` | True | ID пользователя |
| `pin` | form | `string` | True | Пин-код из 4–8 цифр |
| `device_id` | form | `string` | True | ID устройства |
| `device_name` | form | `string` | True | Название устройства |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `logoff`

`GET /v1/logoff`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе всегда передается true |

## `move_to_card`

`POST /v1/moveToCard`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора |
| `card_id` | form | `string` | True | ID карты |
| `amount` | form | `string` | True | Сумма |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `move_to_contract`

`POST /v1/moveToContract`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора |
| `card_id` | form | `string` | True | ID карты |
| `amount` | form | `string` | True | Сумма |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `order_cards`

`POST /v2/orderCards`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `count` | form | `string` | True | Количество карт |
| `office_id` | form | `string` | True | ID офиса продаж (Берется из справочника Office) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `order_documents_email`

`POST /v2/documents`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `id` | json | `json` | True | ID документов |
| `format` | json | `string` | True | Формат документа (pdf/xlsx) |
| `emails` | json | `json` | True | Список email – адресов, на которые будут отправлены документы (до 5) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `order_invoice`

`POST /v2/invoice`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID контракта (Можно передать в заголовке запроса, а не только в URI - строке) |
| `sum` | form | `string` | True | Сумма в рублях |
| `email` | form | `string` | True | Емейл |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `order_report`

`POST /v2/reports`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `id` | json | `string` | True | ID отчета (ID отчетов находятся в поле id метода Список доступных отчетов) |
| `format` | json | `string` | True | Формат отчета (доступные форматы находятся в поле formats метода Список доступных отчетов) |
| `emails` | json | `[string,string]` | False | Список емейлов |
| `params` | json | `json` | True | Параметры отчета (параметры находятся в поле parameters метода Список доступных отчетов) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.job_id` | `[string]` | False | Номер задания (не приходит при заказе на email) |

## `order_report_v1`

`GET /v1/reports`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора |
| `group_id` | query | `[string,string]` | False | Список ID группы карт. Если данный параметр пустой или не передан – будет сформирован отчет либо по списку карт, если указан cards_list, либо по всем картам для указанного договора |
| `cards_list` | query | `[string,string]` | False | Список 16-значных номеров карт по данному договору, по которым должен быть сформирован отчет. Если данный параметр пустой или не передан,то будет сформирован отчет либо по группе карт, если указан group_id, либо по всем картам для указанного договора |
| `start` | query | `string` | True | Дата начала отчетного периода |
| `end` | query | `string` | True | Дата окончания отчетного периода |
| `email` | query | `string` | True | Адреса для отправки на email |
| `report_format` | query | `string` | True | Формат отчета, необходимо передавать "xlsx" "xml" "pdf" "csv" |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `[string]` | True | Номер задания Job_ID |

## `prolong_invite`

`POST /v2/invites/{invite_id}/prolong_free`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

`POST /v2/invites/{invite_id}/prolong`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `release_virtual_card`

`POST /v2/cards/release`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | form | `string` | False | ID договора (Можно передать в заголовке запроса, а не только в URI - строке) Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `template_id` | form | `string` | conditional | ID шаблона ВК Обязателен, если не указан type - Тип карты Не указывать, если указан type - Тип карты |
| `type` | form | `string` | conditional | Тип карты (limit – лимитная схема, wallet – электронный кошелек) Обязателен, если не указан template_id - ID шаблона Не указывать, если указан template_id - ID шаблона |
| `user_id` | form | `string` | False | ID пользователя (Если указан, то выпущенная карта будет привязана к указанному клиенту) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.id` | `string` | True | ID карты |
| `data.number` | `string` | False | Номер карты |
| `data.carrier` | `string` | False | Тип карты |
| `data.product` | `string` | False | Тип продукта карты |
| `data.status` | `string` | False | Статус карты |

## `remove_card_group`

`POST /v1/removeCardGroup`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора |
| `group_id` | form | `string` | True | ID группы карт |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе всегда передается true |

## `remove_limit`

`POST /v1/removeLimit`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора. |
| `limit_id` | form | `string` | True | ID продуктового лимита. |
| `group_id` | form | `string` | False | ID группы карт. Если ID группы карты не передано, то будет удален лимит по карте. Если передан ID группы карт, то будет удален лимит по группе карт |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `remove_region_limit`

`POST /v1/removeRegionLimit`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `regionlimit_id` | form | `string, string` | True | ID регионального лимита |
| `group_id` | form | `string` | False | ID группы карт. Если ID группы карты не передано, то будет удален региональный лимит по карте. Если передан ID группы карт, то будет удален региональный лимит по группе карт |
| `contract_id` | header | `string` | True | ID договора |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `remove_restriction`

`POST /v1/removeRestriction`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `restriction_id` | form | `string,string` | True | ID товарного ограничителя |
| `group_id` | form | `string` | False | ID группы карт. Если ID группы карты не передано, будет удален лимит по карте. Если передан ID группы карт, то будет удален лимит по группе карт |
| `contract_id` | header | `string` | True | ID договора |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `resend_invite`

`GET /v2/invites/{invite_id}/send`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.id` | `string` | True | ID приглашения |
| `data.url` | `string` | True | Уникальная ссылка для регистрации |
| `data.attempts` | `uint` | True | Количество попыток повторных отправок в день |
| `data.expired_at` | `timestamp` | True | Дата окончания |

## `reset_mpc`

`POST /v2/cards/{card_id}/resetMPC`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `contract_id` | header | `string` | True | ID договора |
| `type` | form | `string` | False | Тип счетчика; по умолчанию ResetCounterCode |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `reset_pin`

`POST /v2/cards/{card_id}/resetPIN`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `code` | form | `string` | True | Код из Emailа |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `set_card_comment`

`POST /v1/setCardComment`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | form | `string` | True | ID карты |
| `contract_id` | header | `string` | True | ID договора |
| `comment` | form | `string` | True | Комментарий |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `set_card_group`

`POST /v1/setCardGroup`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | form | `string` | True | ID договора |
| `name` | form | `string` | True | Имя группы карт |
| `id` | form | `string` | False | ID группы карт |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data.id` | `string` | True | ID сохранённой группы карт |

## `set_card_product`

`POST /v1/setCardProduct`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора |
| `card_id` | form | `json` | True | ID карт ([“424234”,”423423”]) |
| `product` | form | `string` | True | Тип продукта (wallet или limit) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `[string, string]` | False | ID карт, у которых изменен тип продукта |

## `set_cards_to_group`

`POST /v1/setCardsToGroup`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | header | `string` | True | ID договора |
| `group_id` | form | `string` | True | ID группы карт |
| `cards_list` | form | `json` | True | Cписок ID карт по данному договору, добавляемых или удаляемых из группы карт |
| `cards_list.id` | form | `string` | True | ID карты |
| `cards_list.type` | form | `string` | True | Действие. Может принимать значения: Attach – добавить карту в группу. Detach – удалить карту из группы |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе всегда передается true |

## `set_limit`

`POST /v1/setLimit`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `limit` | form | `json` | True | Массив данных лимита |
| `limit[].id` | form | `string` | False | ID лимита |
| `limit[].card_id` | form | `string` | False | ID карты |
| `limit[].group_id` | form | `string` | False | ID группы карт |
| `limit[].contract_id` | form | `string` | True | ID договора |
| `limit[].productGroup` | form | `string` | False | ID группы продукта |
| `limit[].productType` | form | `string` | True | ID типа продукта |
| `limit[].amount` | form | `json` | False | Ограничение по количеству |
| `limit[].sum` | form | `json` | False | Ограничение по сумме |
| `limit[].term` | form | `json` | True | Ограничение по времени |
| `limit[].time` | form | `json` | True | Длительность, период времени |
| `limit[].transactions` | form | `json` | False | Ограничение по числу транзакций за период |
| `limit[].amount.unit` | form | `string` | True | Единица измерения |
| `limit[].amount.value` | form | `uint` | True | Суммарное количество ограничения |
| `limit[].sum.currency` | form | `string` | True | Валюта |
| `limit[].sum.value` | form | `uint` | True | Суммарный размер ограничения |
| `limit[].term.days` | form | `string[7]` | False | Строка из 7 нулей и единиц. 1 – ограничение применяется в этот день, 0 – нет |
| `limit[].term.time` | form | `json` | False | Время обслуживания |
| `limit[].term.type` | form | `uint` | True | Способ применения ограничения: 1 – Ограничение применяется всегда (во все указанные дни недели). 2 – Ограничение применяется только в рабочие дни. 3 – Ограничение применяется только в выходные и праздничные дни |
| `term.time.from` | form | `string` | True | От |
| `term.time.to` | form | `string` | True | До |
| `limit[].term.time.number` | form | `uint` | True | Значение. |
| `limit[].term.time.type` | form | `uint` | True | Период действия ограничения. 2 – Разовый, 3 – Сутки, 4 – Неделя, 5 – Месяц, 6 – Квартал, 7 – Год |
| `limit[].transactions.count` | form | `uint` | True | Количество транзакций по услуге |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `[string]` | True | ID сохраненного лимита |

## `set_region_limit`

`POST /v1/setRegionLimit`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `region_limit` | form | `json` | True | Массив параметров |
| `restriction.id` | form | `string` | False | ID регионального лимита |
| `restriction.card_id` | form | `string` | False | ID карты |
| `restriction.group_id` | form | `string` | False | ID группы карт |
| `restriction.contract_id` | form | `string` | False | ID договора. Если ID договора не указан, то выбирается первый из всех договоров пользователя |
| `restriction.country` | form | `string` | True | Код страны обслуживания |
| `restriction.region` | form | `string` | False | Код регион обслуживания |
| `restriction.service_center` | form | `string` | False | ID АЗС |
| `restriction.partner` | form | `string` | False | ID партнера |
| `restriction.limit_type` | form | `uint` | True | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель. |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `[string]` | False | ID сохранённого регионального лимита |

## `set_restriction`

`POST /v1/setRestriction`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `restriction` | form | `json` | True | Массив параметров |
| `restriction[].id` | form | `string` | False | ID товарного ограничителя |
| `restriction[].card_id` | form | `string` | False | ID карты |
| `restriction[].group_id` | form | `string` | False | ID группы карт |
| `restriction[].contract_id` | form | `string` | True | ID договора |
| `restriction[].productGroup` | form | `string` | False | ID группы продукта |
| `restriction[].productType` | form | `string` | True | ID типа продукта |
| `restriction[].restriction_type` | form | `uint` | True | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `[string]` | True | ID сохраненного ограничителя |

## `update_mpc`

`POST /v2/cards/{card_id}/updateMPC`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `card_id` | path | `string` | True | ID карты |
| `contract_id` | header | `string` | True | ID договора |
| `pin` | form | `string` | True | Пин-код МПК |
| `new_pin` | form | `string` | False | Новый пин-код; если не указан |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |

## `update_template`

`POST /v2/vc/templates/{template_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `name` | form | `string` | True | Имя шаблона ВК (Уникальное в рамках договора) |
| `type` | form | `string` | True | Тип карты (Limit – лимитная схема, Wallet – электронный кошелек) |
| `contract_id` | header | `string` | True | ID договора (Изменить нельзя) |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID шаблона |

## `update_template_georestriction`

`POST /v2/vc/templates/{template_id}/georestrictions/{georestriction_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | json | `string` | True | ID договора (Изменить нельзя) |
| `country` | json | `string` | True | ID страны |
| `region` | json | `string` | False | ID региона |
| `partner` | json | `string` | False | ID партнера |
| `service_center` | json | `string` | False | ID АЗС |
| `restriction_type` | json | `uint` | True | 1 – Разрешающий геоограничитель, 2 – Запрещающий геоограничитель |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID геоограничителя |

## `update_template_limit`

`POST /v2/vc/templates/{template_id}/limits/{limit_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | json | `string` | True | ID договора (Изменить нельзя) |
| `amount` | json | `json` | conditional | Ограничение по количеству (Обязательный параметр, если не заполнено sum) |
| `sum` | json | `json` | conditional | Ограничение по сумме (Обязательный параметр, если не заполнено amount) |
| `time` | json | `json` | True | Длительность, период времени |
| `product_type` | json | `string` | True | ID типа продукта |
| `product_group` | json | `string` | False | ID группы продукта |
| `amount.unit` | json | `string` | True | Единица измерения |
| `amount.value` | json | `float` | True | Суммарное количество ограничения |
| `sum.currency` | json | `string` | True | Валюта |
| `sum.value` | json | `float` | True | Суммарный размер ограничения |
| `time.number` | json | `uint` | True | Значение |
| `time.type` | json | `uint` | True | Период действия ограничения: 2 – Разовый, 3 – Сутки, 4 – Неделя, 5 – Месяц, 6 – Квартал, 7 – Год |
| `term.days` | json | `string[7]` | False | Строка из 7 нулей и единиц. 1 – ограничение применяется в этот день, 0 – нет |
| `term.time` | json | `json` | False | Время обслуживания |
| `term.type` | json | `uint` | True | Способ применения ограничения. 1 - Ограничение применяется всегда (во все указанные дни недели) 2 - Ограничение применяется только в рабочие дни 3 - Ограничение применяется только в выходные и праздничные дни |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID лимита |

## `update_template_restriction`

`POST /v2/vc/templates/{template_id}/restrictions/{restriction_id}`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| `contract_id` | json | `string` | True | ID договора (Изменить нельзя) |
| `product_type` | json | `string` | True | ID типа продукта |
| `product_group` | json | `string` | False | ID группы продукта |
| `restriction_type` | json | `uint` | True | 1 – Разрешающий ограничитель, 2 – Запрещающий ограничитель |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `string` | True | ID ограничителя |

## `verify_pin`

`POST /v2/cards/{card_id}/verifyPIN`

### Запрос

| Путь | Расположение | Тип | Обяз. | Описание |
|---|---|---|---|---|
| — | — | — | — | Параметры метода отсутствуют |

### Ответ

| Путь | Тип | Обяз. | Описание |
|---|---|---|---|
| `status` | `json` | True | Статус выполнения запроса. |
| `status.code` | `uint` | True | Код результата выполнения запроса. |
| `status.errors` | `json` | False | Массив ошибок. |
| `timestamp` | `uint` | False | Время ответа. |
| `data` | `bool` | True | При успехе передается true |
