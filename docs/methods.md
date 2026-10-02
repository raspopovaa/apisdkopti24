---
description: "Каталог методов apisdkopti24: параметры, маршруты, типы ответов и примеры."
---

# Методы API

Документация генерируется из runtime registry, публичных сигнатур, type hints, моделей SDK и описаний методов API.

!!! info "Покрытие"
    Опубликовано **89 операций** из 89, зарегистрированных в SDK.
    Каталог включает операции корпоративного API и подтверждённые методы МПК/QR.

| Сервис | Операций | Назначение |
|---|---:|---|
| [`client.auth`](methods/auth.md) | 3 | Авторизация и сведения о сессии |
| [`client.card_groups`](methods/card_groups.md) | 4 | Группы топливных карт |
| [`client.cards`](methods/cards.md) | 9 | Топливные карты |
| [`client.contracts`](methods/contracts.md) | 7 | Договоры и документы |
| [`client.dictionaries`](methods/dictionaries.md) | 4 | Справочники и торговые точки |
| [`client.ewallet`](methods/ewallet.md) | 3 | Электронный кошелек |
| [`client.final_prices`](methods/final_prices.md) | 2 | Расчет итоговой стоимости |
| [`client.invites`](methods/invites.md) | 5 | Приглашения пользователей |
| [`client.limits`](methods/limits.md) | 3 | Продуктовые лимиты |
| [`client.region_limits`](methods/region_limits.md) | 3 | Региональные ограничения |
| [`client.reports`](methods/reports.md) | 7 | Отчеты |
| [`client.restrictions`](methods/restrictions.md) | 3 | Ограничители обслуживания |
| [`client.templates`](methods/templates.md) | 16 | Шаблоны виртуальных карт |
| [`client.transactions`](methods/transactions.md) | 4 | Транзакции |
| [`client.users`](methods/users.md) | 7 | Пользователи и водители |
| [`client.virtual_cards`](methods/virtual_cards.md) | 9 | Виртуальные карты и QR |

## Общий формат ответа

Большинство методов возвращают типизированную модель SDK. Ответ проходит проверку Pydantic: обязательные поля, типы, вложенные модели, ограничения схемы и пользовательские валидаторы.

Подробные структуры и фактические правила проверки приведены в разделе [Типы данных](data-types/index.md).

## Свод методов API

Сводная таблица всех методов API из документа «Свод методов API с описанием» от 18.12.2025: название, назначение и роли учётной записи. Маршрут, доступность на DEMO и тарификация совпадают с колонками «Маршрут» на страницах сервисов.

!!! note "Роли проверяет сервер"
    Колонка «Роли» показывает, учётной записи с какой ролью сервер разрешает вызывать метод. SDK роль не проверяет: если у токена недостаточно прав, сервер вернёт `403`, и SDK поднимет `AccessDeniedError`. Токены API выдаются учётным записям с ролью «Администратор» или «Чтение».

Методов API 91, а операций SDK 89: `create_invite` и `prolong_invite` покрывают по два метода API — какой вызвать, задаёт `with_send`. По умолчанию (`with_send=True`) приглашение отправляется по SMS/e-mail и запрос тарифицируется; `with_send=False` вызывает бесплатный вариант без отправки.

### Пользователь, учетная запись

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Авторизация пользователя (`authuser`) | [`auth.auth_user`](methods/auth.md#clientauthauth_user) | `POST v1/authUser` | Да | Нет | Администратор, Чтение | Метод используется для авторизации в системе через API. При выполнении запроса пользователь получает идентификатор активной сессии, который используется во всех последующих запросах для возможности их выполнения. Суть метода заключается в том же, что и авторизация в ЛК (т.е. получение прав на работу в интерфейсе). |
| Деавторизация пользователя (`logoff`) | [`auth.logoff`](methods/auth.md#clientauthlogoff) | `GET v1/logoff` | Да | Нет | Администратор, Чтение | Метод делает ранее полученную сессию (на этапе авторизации) неактивной. Другими словами, пользователь "выходит" из профиля (аналогично кнопке выхода в ЛК). |
| Статистика (`info`) | [`auth.get_info`](methods/auth.md#clientauthget_info) | `GET v1/info` | Да | Нет | Администратор, Чтение | Получение статистических данных по вызовам всех методов. |

### Договор — Contract

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Данные по договору (`getpartcontractdata`) | [`contracts.get_contract_data`](methods/contracts.md#clientcontractsget_contract_data) | `GET v1/getPartContractData` | Да | Да | Администратор, Чтение | Получение данных по договору (статус, менеджер, доступный остаток, расход в текущем месяце, число карт и пр.). |
| Платежи по договору (`getpayments`) | [`contracts.get_payments`](methods/contracts.md#clientcontractsget_payments) | `GET v1/getPayments` | Да | Да | Администратор, Чтение | Получение данных о платежах. |
| Список первичных документов по договору за период (`documents_get`) | [`contracts.get_documents`](methods/contracts.md#clientcontractsget_documents) | `GET v2/documents` | Нет | Нет | Администратор | Получение списка первичных документов (номер документа, дата, сумма, НДС, номер договора и пр.). |
| Заказ первичных документов на почту (`documents_post`) | [`contracts.order_documents_email`](methods/contracts.md#clientcontractsorder_documents_email) | `POST v2/documents` | Нет | Да | Администратор | Заказ первичных документов по ID документа на указанные email-адреса (до 5 адресов). |
| Заказ топливных карт (`order_cards`) | [`contracts.order_cards`](methods/contracts.md#clientcontractsorder_cards) | `POST v2/orderCards` | Нет | Да | Администратор | Заказ необходимого количества топливных карт в определенном офисе продаж. |
| Заказ счета на оплату (`invoice`) | [`contracts.order_invoice`](methods/contracts.md#clientcontractsorder_invoice) | `POST v2/invoice` | Нет | Нет | Администратор, Чтение | Заказ счета на оплату. |
| Счета на оплату (`invoices`) | [`contracts.get_invoices`](methods/contracts.md#clientcontractsget_invoices) | `GET v2/invoices` | Да | Нет | Администратор, Чтение | Получение списка счетов на оплату. |

### Топливные карты — Cards

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список карт договора (v.2) (`cards_cache`) | [`cards.get_cards_v2`](methods/cards.md#clientcardsget_cards_v2) | `GET v2/cards` | Да | Нет | Администратор, Чтение | Новый метод получения списка карт с данными (например: название группы карт, статус, комментарий, существует ли МПК). |
| Список топливных карт (Процессинг) (`cards`) | [`cards.get_cards_v1`](methods/cards.md#clientcardsget_cards_v1) | `GET v1/cards` | Да | Да | Администратор, Чтение | Получение списка карт с данными (например: комментарий, дата последнего использования, минимальное время между транзакциями, тип продукта - лимитная или ЭК). |
| Список топливных карт по группе карт (`cards_group`) | [`cards.get_cards_by_group`](methods/cards.md#clientcardsget_cards_by_group) | `GET v1/cards` | Нет | Нет | Администратор, Чтение | Получение списка по группе карт. |
| Список водителей по карте (`cards_drivers`) | [`cards.get_card_drivers`](methods/cards.md#clientcardsget_card_drivers) | `GET v2/cards/{card_id}/drivers` | Да | Да | Администратор, Чтение | Получение списка водителей. |
| Детальная информация по карте (`cards_detail`) | [`cards.get_card_detail`](methods/cards.md#clientcardsget_card_detail) | `GET v1/cards` | Да | Да | Администратор, Чтение | Получение детальной информации по карте (дата выпуска, тип продукта, тип карты и пр.). |
| Блокировка и разблокировка карты (`blockcard`) | [`cards.block_card`](methods/cards.md#clientcardsblock_card) | `POST v1/blockCard` | Да | Да | Администратор | Блокировка и разблокировка карты. |
| Установить комментарий на топливную карту (`setcardcomment`) | [`cards.set_card_comment`](methods/cards.md#clientcardsset_card_comment) | `POST v1/setCardComment` | Да | Да | Администратор | Установка комментария на карту. |
| Запрос одноразового кода для сброса попыток ввода PIN карты (`cards_verify_pin`) | [`cards.verify_pin`](methods/cards.md#clientcardsverify_pin) | `POST v2/cards/{card_id}/verifyPIN` | Да | Нет | Администратор | Данный метод позволяет инициировать запрос на сброс попыток некорректного ввода PIN-кода карты. Вам будет отправлено письмо с кодом подтверждения на почту, которая привязана к вашей учетной записи. Данный код нужно ввести в метод "Подтверждение сброса попыток некорректного ввода PIN - кода карты" для завершения операции сброса попыток. |
| Подтверждение сброса попыток некорректного ввода PIN - кода карты (`cards_reset_pin`) | [`cards.reset_pin`](methods/cards.md#clientcardsreset_pin) | `POST v2/cards/{card_id}/resetPIN` | Нет | Да | Администратор | Данный метод позволяет завершить операцию со сбросом попыток некорректного ввода PIN – кода пластиковой топливной карты на АЗС. Код подтверждения будет отправлен на почту, которая привязана к вашей учетной записи. |

### Электронный кошелек — Ewallet

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Изменить тип продукта карты (`setcardproduct`) | [`ewallet.set_card_product`](methods/ewallet.md#clientewalletset_card_product) | `POST v1/setCardProduct` | Да | Да | Администратор | Изменение типа продукта на карте: «лимитная карта»/«электронный кошелек». |
| Перевести деньги с договора на кошелек (`movetocard`) | [`ewallet.move_to_card`](methods/ewallet.md#clientewalletmove_to_card) | `POST v1/moveToCard` | Да | Да | Администратор | Перевод денежных средств с договора на кошелек. |
| Перевести деньги с кошелька на договор (`movetocontract`) | [`ewallet.move_to_contract`](methods/ewallet.md#clientewalletmove_to_contract) | `POST v1/moveToContract` | Да | Да | Администратор | Перевод денежных средств с кошелька на договор. |

### Транзакции — Transactions

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список последних транзакций по договору и карте (`transactions`) | [`transactions.get_transactions_v1`](methods/transactions.md#clienttransactionsget_transactions_v1) | `GET v1/transactions` | Нет | Да | Администратор, Чтение | Получение списка последних 30 транзакций по договору или по карте (устаревший метод). Данные о транзакциях поступают в реальном времени, однако в этом случае будут возвращаться все данные – информация о транзакциях в их текущем статусе (например, транзакция может находиться в статусе обработки). |
| Список транзакций по договору (v.2) (`contract_transactions`) | [`transactions.get_transactions_v2`](methods/transactions.md#clienttransactionsget_transactions_v2) | `GET v2/transactions` | Да | Да | Администратор, Чтение | Получение списка транзакций по договору за выбранный период не больше месяца. Новые транзакции доступны спустя 1 – 2 часа (время постирования в системе) после их проведения. Указанное время является примерным и может быть увеличено в отдельных случаях. |
| Данные по транзакции (`transaction_detail`) | [`transactions.get_transaction_detail`](methods/transactions.md#clienttransactionsget_transaction_detail) | `GET v2/transactions/{transaction_id}` | Да | Нет | Администратор, Чтение | Метод возвращает данные по конкретной транзакции (дата, время, продукт, цена, количество, сумма и пр.) по её ID. |
| Список транзакций по карте (v.2) (`card_transactions`) | [`transactions.get_card_transactions_v2`](methods/transactions.md#clienttransactionsget_card_transactions_v2) | `GET v2/cards/{card_id}/transactions` | Да | Да | Администратор, Чтение | Получение списка транзакций по карте за выбранный период не больше месяца. Новые транзакции доступны спустя 1 – 2 часа (время постирования в системе) после их проведения. Указанное время является примерным и может быть увеличено в отдельных случаях. |

### Продуктовые лимиты — Limit

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список продуктовых лимитов по договору, карте и группе карт (`limit`) | [`limits.get_limits`](methods/limits.md#clientlimitsget_limits) | `GET v1/limit` | Да | Нет | Администратор, Чтение | Получение списка продуктовых лимитов. |
| Удаление продуктового лимита по карте и группе карт (`removelimit`) | [`limits.remove_limit`](methods/limits.md#clientlimitsremove_limit) | `POST v1/removeLimit` | Да | Да | Администратор | Удаление продуктового лимита. |
| Установка/Изменение продуктового лимита по карте и группе карт (`setlimit`) | [`limits.set_limit`](methods/limits.md#clientlimitsset_limit) | `POST v1/setLimit` | Да | Да | Администратор | Создание/изменение продуктового лимита. |

### Товарные ограничители — Restriction

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список товарных ограничителей по договору, карте и группе карт (`restriction`) | [`restrictions.get_restrictions`](methods/restrictions.md#clientrestrictionsget_restrictions) | `GET v1/restriction` | Да | Да | Администратор, Чтение | Получение списка товарных ограничителей. |
| Удаление товарного ограничителя по карте и группе карт (`removerestriction`) | [`restrictions.remove_restriction`](methods/restrictions.md#clientrestrictionsremove_restriction) | `POST v1/removeRestriction` | Да | Да | Администратор | Удаление товарного ограничителя. |
| Установка/Изменение товарного ограничителя по карте и группе карт (`setrestriction`) | [`restrictions.set_restriction`](methods/restrictions.md#clientrestrictionsset_restriction) | `POST v1/setRestriction` | Нет | Да | Администратор | Создание/изменение товарного ограничителя. |

### Региональные лимиты — RegionLimit

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список региональных лимитов по договору, карте и группе карт (`regionlimit`) | [`region_limits.get_region_limits`](methods/region_limits.md#clientregion_limitsget_region_limits) | `GET v1/regionLimit` | Да | Да | Администратор, Чтение | Получение списка региональных лимитов. |
| Удаление регионального лимита по карте и группе карт (`removeregionlimit`) | [`region_limits.remove_region_limit`](methods/region_limits.md#clientregion_limitsremove_region_limit) | `POST v1/removeRegionLimit` | Да | Да | Администратор | Удаление регионального лимита. |
| Установка/Изменение регионального лимита по карте и группе карт (`setregionlimit`) | [`region_limits.set_region_limit`](methods/region_limits.md#clientregion_limitsset_region_limit) | `POST v1/setRegionLimit` | Да | Да | Администратор | Установка/изменение регионального лимита. |

### Группа карт — CardGroup

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Добавление карт в группу карт (`setcardstogroup`) | [`card_groups.set_cards_to_group`](methods/card_groups.md#clientcard_groupsset_cards_to_group) | `POST v1/setCardsToGroup` | Да | Да | Администратор | Добавление карт в группу карт. |
| Список групп карт (`cardgroups`) | [`card_groups.get_card_groups`](methods/card_groups.md#clientcard_groupsget_card_groups) | `GET v1/cardGroups` | Да | Нет | Администратор, Чтение | Получение списка групп карт. |
| Удаление группы карт (`removecardgroup`) | [`card_groups.remove_card_group`](methods/card_groups.md#clientcard_groupsremove_card_group) | `POST v1/removeCardGroup` | Да | Да | Администратор | Удаление группы карт. |
| Установка/Изменение группы карт (`setcardgroup`) | [`card_groups.set_card_group`](methods/card_groups.md#clientcard_groupsset_card_group) | `POST v1/setCardGroup` | Да | Да | Администратор | Создание/изменение группы карт. |

### Запрос отчета — Reports

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список доступных отчетов (v.2) (`reports_get`) | [`reports.get_reports`](methods/reports.md#clientreportsget_reports) | `GET v2/reports` | Да | Нет | Администратор, Чтение | Получение списка всех доступных отчетов с параметрами. |
| Заказ отчета на email и по ссылке (v.2) (`reports_post`) | [`reports.order_report`](methods/reports.md#clientreportsorder_report) | `POST v2/reports` | Да | Да | Администратор, Чтение | Новый метод, предоставляет возможность заказа любого из доступных видов отчетов. Список доступных видов отчетов предоставляется методом «Список доступных отчетов (v.2)». Ограничения отправки отчетов на Email составляет 15мб. Новые транзакции доступны спустя 1 – 2 часа (время постирования в системе) после их проведения. Указанное время является примерным и может быть увеличено в отдельных случаях. |
| Список ранее заказанных отчетов по ссылке (v.2) (`reports_jobs`) | [`reports.get_report_jobs`](methods/reports.md#clientreportsget_report_jobs) | `GET v2/reports/jobs` | Да | Нет | Администратор, Чтение | Метод предоставляет доступ к идентификаторам ранее заказанных отчетов, которые используются для генерации файлов отчетов, то есть только информацию о ранее заказанных отчетах, но не сами файлы отчетов. После заказа можно запросить все отчеты, заказанные по ссылке в последние 14 дней и повторно их скачать. |
| Генерация файла отчета (v.2) (`reports_jobs_file`) | [`reports.download_report_file`](methods/reports.md#clientreportsdownload_report_file) | `GET v2/reports/jobs/{job_id}` | Нет | Да | Администратор, Чтение | Метод предоставляет возможность получить содержимое файла заказанного ранее отчета. В запросе по данному методу передается идентификатор ранее заказанного отчета, в ответе возвращается содержимое файла, которое используется для формирования файла отчета. Получение файла отчета в необходимом клиенту формате (pdf, xlsx, csv, xml и другие). |
| Запрос транзакционного отчета за период на email и по ссылке (`reports`) | [`reports.order_report_v1`](methods/reports.md#clientreportsorder_report_v1) | `GET v1/reports` | Нет | Да | Администратор, Чтение | Устаревший метод, т.к. позволяет заказать только транзакционный отчет по договору на email. Ограничения отправки отчетов на Email составляет 15мб. Новые транзакции доступны спустя 1 – 2 часа (время постирования в системе) после их проведения. Указанное время является примерным и может быть увеличено в отдельных случаях. |
| Список ранее заказанных отчетов по ссылке (`getreportjoblist`) | [`reports.get_report_job_list_v1`](methods/reports.md#clientreportsget_report_job_list_v1) | `GET v1/getReportJobList` | Да | Нет | Администратор, Чтение | Метод предоставляет доступ к идентификаторам ранее заказанных транзакционных отчетов, которые используются для генерации файлов отчетов, то есть только информацию о ранее заказанных отчетах, но не сами файлы отчетов. После заказа можно запросить все транзакционные отчеты, заказанные по ссылке в последние 7 дней и повторно их скачать. |
| Генерация файла отчета (`getreportfile`) | [`reports.download_report_file_v1`](methods/reports.md#clientreportsdownload_report_file_v1) | `GET v1/getReportFile` | Нет | Да | Администратор, Чтение | Метод предоставляет возможность получить содержимое файла заказанного ранее транзакционного отчета. В запросе по данному методу передается идентификатор ранее заказанного отчета, в ответе возвращается содержимое файла, которое используется для формирования файла отчета. Получение файла отчета в необходимом клиенту формате (pdf, xlsx, csv, xml и другие). |

### Приглашение пользователей — Invites

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список приглашений (`invites_get`) | [`invites.get_invites`](methods/invites.md#clientinvitesget_invites) | `GET v2/invites` | Да | Нет | Администратор | Получение списка приглашений. |
| Создание приглашения с отправкой (`invites_post`) | [`invites.create_invite`](methods/invites.md#clientinvitescreate_invite) | `POST v2/invites` | Нет | Да | Администратор | Создание приглашения - генерация ссылки для регистрации пользователя - с отправкой по SMS/E-mail (ссылка действует 3 календарных дня). С помощью приглашения можно зарегистрировать, например, водителя и сразу привязать шаблон виртуальной карты, либо привязать физические топливные карты. |
| Создание приглашения (`invites_post_free`) | [`invites.create_invite`](methods/invites.md#clientinvitescreate_invite) | `POST v2/invites_free` | Да | Нет | Администратор | Создание приглашения - генерация ссылки для регистрации пользователя. С помощью приглашения можно зарегистрировать, например, водителя и сразу привязать шаблон виртуальной карты, либо привязать физические топливные карты. |
| Удалить приглашение (`invites_delete`) | [`invites.delete_invite`](methods/invites.md#clientinvitesdelete_invite) | `DELETE v2/invites/{invite_id}` | Да | Нет | Администратор | Удаление приглашения. |
| Повторная отправка приглашения (`invites_send`) | [`invites.resend_invite`](methods/invites.md#clientinvitesresend_invite) | `GET v2/invites/{invite_id}/send` | Нет | Да | Администратор | Повторная отправка приглашения. |
| Продлить приглашение с отправкой (`invites_prolong`) | [`invites.prolong_invite`](methods/invites.md#clientinvitesprolong_invite) | `POST v2/invites/{invite_id}/prolong` | Нет | Да | Администратор | Продление приглашения на 7 дней, отправка по SMS/E-mail. |
| Продлить приглашение (`invites_prolong_free`) | [`invites.prolong_invite`](methods/invites.md#clientinvitesprolong_invite) | `POST v2/invites/{invite_id}/prolong_free` | Да | Нет | Администратор | Продление приглашения на 7 дней. |

### Пользователи — Users

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список пользователей (`users_get`) | [`users.get_users`](methods/users.md#clientusersget_users) | `GET v2/users` | Да | Нет | Администратор | Получение списка пользователей с указанием роли. |
| Создание водителя без персональных данных (`users_post`) | [`users.create_user`](methods/users.md#clientuserscreate_user) | `POST v2/users` | Да | Да | Администратор | Создание «технического» водителя без ФИО (персональных данных), чтобы использовать их для дальнейших интеграций. Реальных водителей следует создавать через приглашение пользователей |
| Прикрепление договоров к пользователю (`users_attach_contracts`) | [`users.attach_contracts`](methods/users.md#clientusersattach_contracts) | `POST v2/users/{user_id}/attachContracts` | Да | Да | Администратор | Метод позволяет: А) закрепить уже существующего пользователя за договором; Б) прикрепить к пользователю шаблон ВК (что необходимо для выпуска виртуальных карт); В) разрешить пользователю использование МПК (необходимо для выпуска виртуальных карт и активации МПК по ТК). |
| Открепление договоров от пользователя (`users_detach_contracts`) | [`users.detach_contracts`](methods/users.md#clientusersdetach_contracts) | `POST v2/users/{user_id}/detachContracts` | Да | Да | Администратор | Открепление договоров от пользователя. |
| Прикрепление карты к пользователю (`users_attach_card`) | [`users.attach_card`](methods/users.md#clientusersattach_card) | `POST v2/users/{user_id}/attachCard` | Да | Да | Администратор | Метод позволяет закрепить существующую свободную ТК за пользователем. |
| Открепление карты от пользователя (`users_detach_card`) | [`users.detach_card`](methods/users.md#clientusersdetach_card) | `POST v2/users/{user_id}/detachCard` | Да | Да | Администратор | Метод позволяет открепить карту от пользователя. |
| Удаление пользователя (`users_delete`) | [`users.delete_user`](methods/users.md#clientusersdelete_user) | `DELETE v2/users/{user_id}` | Да | Да | Администратор | Метод позволяет удалить пользователя. В CRM при этом для контактного лица будет выставлен статус «Неактивный». |

### Шаблоны ВК — Templates

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список шаблонов ВК (`vc_templates_get`) | [`templates.get_templates`](methods/templates.md#clienttemplatesget_templates) | `GET v2/vc/templates` | Да | Нет | Администратор | Получение списка шаблонов виртуальных карт. Шаблон – это первоначальные параметры (Тип карты, Лимиты, Ограничители), с которыми будет выпущена эта ВК, и все последующие, если использовать этот шаблон. |
| Создание шаблона ВК (`vc_templates_post`) | [`templates.create_template`](methods/templates.md#clienttemplatescreate_template) | `POST v2/vc/templates` | Да | Да | Администратор | Создание шаблона виртуальной карты. Шаблон – это первоначальные параметры (Тип карты, Лимиты, Ограничители), с которыми будет выпущена эта ВК, и все последующие, если использовать этот шаблон. |
| Изменение шаблона ВК (`vc_templates_put`) | [`templates.update_template`](methods/templates.md#clienttemplatesupdate_template) | `PUT v2/vc/templates/{template_id}` | Да | Да | Администратор | Изменение шаблона виртуальной карты. |
| Удаление шаблона ВК (`vc_templates_delete`) | [`templates.delete_template`](methods/templates.md#clienttemplatesdelete_template) | `DELETE v2/vc/templates/{template_id}` | Да | Да | Администратор | Удаление шаблона виртуальной карты. |
| Список лимитов шаблона ВК (`vc_templates_limits_get`) | [`templates.get_template_limits`](methods/templates.md#clienttemplatesget_template_limits) | `GET v2/vc/templates/{template_id}/limits` | Да | Нет | Администратор | Получение списка лимитов шаблона виртуальной карты. |
| Создание лимита шаблона ВК (`vc_templates_limits_post`) | [`templates.create_template_limit`](methods/templates.md#clienttemplatescreate_template_limit) | `POST v2/vc/templates/{template_id}/limits` | Да | Да | Администратор | Создание лимита шаблона виртуальной карты. |
| Изменение лимита шаблона ВК (`vc_templates_limits_put`) | [`templates.update_template_limit`](methods/templates.md#clienttemplatesupdate_template_limit) | `PUT v2/vc/templates/{template_id}/limits/{limit_id}` | Да | Да | Администратор | Изменение лимита шаблона виртуальной карты. |
| Удаление лимита шаблона ВК (`vc_templates_limits_delete`) | [`templates.delete_template_limit`](methods/templates.md#clienttemplatesdelete_template_limit) | `DELETE v2/vc/templates/{template_id}/limits/{limit_id}` | Да | Да | Администратор | Удаление лимита шаблона виртуальной карты. |
| Список ограничителей шаблона ВК (`vc_templates_restrictions_get`) | [`templates.get_template_restrictions`](methods/templates.md#clienttemplatesget_template_restrictions) | `GET v2/vc/templates/{template_id}/restrictions` | Да | Нет | Администратор | Получение списка ограничителей шаблона виртуальной карты. |
| Создание ограничителя шаблона ВК (`vc_templates_restrictions_post`) | [`templates.create_template_restriction`](methods/templates.md#clienttemplatescreate_template_restriction) | `POST v2/vc/templates/{template_id}/restrictions` | Да | Да | Администратор | Создание ограничителя шаблона виртуальной карты. |
| Изменение ограничителя шаблона ВК (`vc_templates_restrictions_put`) | [`templates.update_template_restriction`](methods/templates.md#clienttemplatesupdate_template_restriction) | `PUT v2/vc/templates/{template_id}/restrictions/{restrictions_id}` | Да | Да | Администратор | Изменение ограничителя виртуальной карты. |
| Удаление ограничителя шаблона ВК (`vc_templates_restrictions_delete`) | [`templates.delete_template_restriction`](methods/templates.md#clienttemplatesdelete_template_restriction) | `DELETE v2/vc/templates/{template_id}/restrictions/{restrictions_id}` | Да | Да | Администратор | Удаление ограничителя шаблона виртуальной карты. |
| Список геоограничителей шаблона ВК (`vc_templates_georestrictions_get`) | [`templates.get_template_georestrictions`](methods/templates.md#clienttemplatesget_template_georestrictions) | `GET v2/vc/templates/{template_id}/georestrictions` | Да | Нет | Администратор | Получение списка геоограничителей шаблона виртуальной карты. |
| Создание геоограничителя шаблона ВК (`vc_templates_georestrictions_post`) | [`templates.create_template_georestriction`](methods/templates.md#clienttemplatescreate_template_georestriction) | `POST v2/vc/templates/{template_id}/georestrictions` | Да | Да | Администратор | Создание геоограничителя шаблона виртуальной карты. |
| Изменение геоограничителя шаблона ВК (`vc_templates_georestrictions_put`) | [`templates.update_template_georestriction`](methods/templates.md#clienttemplatesupdate_template_georestriction) | `PUT v2/vc/templates/{template_id}/georestrictions/{georestrictions_id}` | Да | Да | Администратор | Изменение геоограничителя шаблона виртуальной карты. |
| Удаление геоограничителя шаблона ВК (`vc_templates_georestrictions_delete`) | [`templates.delete_template_georestriction`](methods/templates.md#clienttemplatesdelete_template_georestriction) | `DELETE v2/vc/templates/{template_id}/georestrictions/{georestrictions_id}` | Да | Да | Администратор | Удаление геоограничителя шаблона виртуальной карты. |

### Виртуальная карта — Virtual Card

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Запрос на выпуск виртуальной карты (`cards_post`) | [`virtual_cards.create_virtual_card`](methods/virtual_cards.md#clientvirtual_cardscreate_virtual_card) | `POST v2/cards` | Нет | Да | Администратор | Устаревший метод выпуска виртуальной карты, подразумевает обязательное наличие шаблона ВК у пользователя. |
| Запрос на выпуск виртуальной карты (v.2) (`release`) | [`virtual_cards.release_virtual_card`](methods/virtual_cards.md#clientvirtual_cardsrelease_virtual_card) | `POST v2/cards/release` | Нет | Да | Администратор | Новый метод выпуска виртуальной карты позволяет выпустить ВК без использования шаблона ВК, передав в запросе type – тип ВК, с которым нужен выпуск карты. |
| Список выпущенных МПК QR (`mpc`) | [`virtual_cards.get_mpc_qr_list`](methods/virtual_cards.md#clientvirtual_cardsget_mpc_qr_list) | `GET v2/MPC` | Нет | Нет | Администратор | Получение всех выпущенных мобильных профилей карты, с помощью которых можно проводить оплаты по QR, списком. Метод может возвращать все МПК или по конкретному договору. |
| Генерация QR кода оплаты (`pay`) | [`virtual_cards.generate_payment_qr`](methods/virtual_cards.md#clientvirtual_cardsgenerate_payment_qr) | `POST v2/cards/{card_id}/pay` | Нет | Нет | Администратор | Создание QR кода оплаты. Имеет срок жизни до 10 минут. По истечении 10 минут код оплаты становится недействительным и не будет приниматься на АЗС, потребуется выпустить новый QR код оплаты. |
| Инициализация выпуска МПК (`init_mpc`) | [`virtual_cards.init_mpc`](methods/virtual_cards.md#clientvirtual_cardsinit_mpc) | `POST v2/cards/{card_id}/initMPC` | Нет | Нет | Администратор | Создание мобильного профиля карты. МПК создается под картой с привязкой к пользователю. |
| Подтверждение выпуска МПК (`confirm_mpc`) | [`virtual_cards.confirm_mpc`](methods/virtual_cards.md#clientvirtual_cardsconfirm_mpc) | `POST v2/cards/{card_id}/confirmMPC` | Нет | Нет | Администратор | С помощью данного метода завершается процесс создания МПК. В него требуется передать СМС – код, который придет на телефон технического водителя. После успешности операции, вы сможете сразу использовать метод оплаты. МПК хранится на нашей стороне и на 1й карте может быть только 1 МПК. |
| Обновление МПК (`update_mpc`) | [`virtual_cards.update_mpc`](methods/virtual_cards.md#clientvirtual_cardsupdate_mpc) | `POST v2/cards/{card_id}/updateMPC` | Нет | Нет | Администратор | С помощью данного метода можно перевыпустить МПК, тем самым сменить ПИН–код или избавиться от ошибок оплаты на АЗС. |
| Удаление МПК (`delete_mpc`) | [`virtual_cards.delete_mpc`](methods/virtual_cards.md#clientvirtual_cardsdelete_mpc) | `POST v2/cards/{card_id}/deleteMPC` | Нет | Нет | Администратор | Удаление мобильного профиля карты. |
| Сброс счетчиков МПК (`reset_mpc`) | [`virtual_cards.reset_mpc`](methods/virtual_cards.md#clientvirtual_cardsreset_mpc) | `POST v2/cards/{card_id}/resetMPC` | Нет | Нет | Администратор | Сброс счетчиков мобильного профиля карты. |

### Конечные цены — Final Prices

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Получение финальных цен на АЗС по карте (`calculate_prices`) | [`final_prices.get_final_prices`](methods/final_prices.md#clientfinal_pricesget_final_prices) | `POST v2/cards/{card_id}/calculatePrices` (в своде — GET) | Нет | Нет | Администратор | Метод позволяет рассчитать конечную цену за товарную позицию с учетом тарифа клиента по договору. Для корректной работы метода необходимо удостовериться, что выбранные позиции товаров можно приобрести по данной карте. |
| Проверка возможности проведения транзакции (`check_purchase`) | [`final_prices.check_purchase`](methods/final_prices.md#clientfinal_pricescheck_purchase) | `POST v2/cards/{card_id}/checkPurchase` (в своде — GET) | Нет | Нет | Администратор | Проверка возможности проведения транзакции с установленным набором продуктов по карте |

### Справочники

| Метод API | Метод SDK | Запрос | DEMO | Тариф | Роли | Описание |
|---|---|---|:---:|:---:|---|---|
| Список торговых точек (`azs`) | [`dictionaries.get_azs_list_v1`](methods/dictionaries.md#clientdictionariesget_azs_list_v1) | `GET v1/AZS` | Да | Нет | Администратор, Чтение | Получение списка торговых точек. |
| Список торговых точек (v.2) (`poi`) | [`dictionaries.get_azs_list_v2`](methods/dictionaries.md#clientdictionariesget_azs_list_v2) | `GET v2/azs` | Нет | Нет | Администратор, Чтение | Новый метод для получения списка торговых точек с расширенной фильтрацией и улучшенной структурой данных. Для выгрузки полного списка ТТ необходимо выполнить запрос без указания фильтров. |
| Запрос списка фильтров торговых точек (`filters`) | [`dictionaries.get_azs_filters`](methods/dictionaries.md#clientdictionariesget_azs_filters) | `GET v2/azs/filters` | Нет | Нет | Администратор, Чтение | Метод для получения списка параметров для фильтрации. |
| Общие справочники (`getdictionary`) | [`dictionaries.get_dictionary`](methods/dictionaries.md#clientdictionariesget_dictionary) | `GET v1/getDictionary` | Да | Нет | Администратор, Чтение | Наименование справочника: CardStatus – Запрос списка статусов карт; ContractStatus – Запрос списка статусов договора; Country – Запрос списка стран; Currency – Запрос списка валют; Goods – Запрос списка топлива для цен на АЗС; PaymentScheme – Запрос списка схем оплаты договора; PaymentTerm – Запрос списка условий оплаты договора; ProductGroup – Запрос списка групп продукта; ProductType – Запрос списка типов продукта; POIType – Запрос списка типов принадлежности АЗС; Region – Запрос списка регионов; Services – Запрос списка услуг на АЗС; Unit – Запрос списка единиц измерения продуктов; Office – Запрос списка офисов продаж; POIPartner – Запрос списка партнеров; DiscountScheme – Запрос списка схем расчета скидки |
