# API 1.1.60 contract audit

## Summary

| Metric | Value |
|---|---:|
| operations | 82 |
| verified_operations | 3 |
| fixtures | 79 |
| issues | 573 |
| blocking_issues | 0 |
| errors | 240 |
| warnings | 202 |
| info | 131 |

## Findings by code

| Code | Count |
|---|---:|
| `fixture_model_validation_failed` | 1 |
| `missing_response_field` | 254 |
| `request_parameter_mapping_missing` | 129 |
| `response_required_mismatch` | 150 |
| `response_type_mismatch` | 37 |
| `sdk_untyped_model_field` | 2 |

## Details

### `attach_card`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `attach_contracts`

- **INFO** `request_parameter_mapping_missing` `sid`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sid; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `template_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=template_id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `use_mpc`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=use_mpc; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `auth_user`

- **INFO** `request_parameter_mapping_missing` `login`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=login; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `password`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=password; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.contracts`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.read_only`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.contracts[].cards_count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.contracts[].one_price`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `block_card`

- **INFO** `request_parameter_mapping_missing` `card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=card_id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **WARNING** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=[string, string]; actual=missing)

### `check_purchase`

- **INFO** `request_parameter_mapping_missing` `contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contract_id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `create_invite`

- **INFO** `request_parameter_mapping_missing` `role`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=role; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `mobile`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=mobile; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `email`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=email; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `cards`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=cards; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `contracts`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contracts; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `contracts[].id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contracts; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `contracts[].template_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contracts; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `role`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=role; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `mobile`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=mobile; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `email`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=email; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `cards`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=cards; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `contracts`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contracts; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `contracts[].id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contracts; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `contracts[].template_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contracts; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.attempts`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.expired_at`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.attempts`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.expired_at`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `create_template`

- **INFO** `request_parameter_mapping_missing` `type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `create_template_georestriction`

- **INFO** `request_parameter_mapping_missing` `country`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=country; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `region`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=region; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `partner`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=partner; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `service_center`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=service_center; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `create_template_limit`

- **INFO** `request_parameter_mapping_missing` `amount`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=amount; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `sum`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `time`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=time; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_type; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_group`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_group; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `create_restriction`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=create_restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `amount.unit`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=amount; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `amount.value`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=amount; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `sum.currency`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `sum.value`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `time.number`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=time; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `time.type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=time; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.days`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.time`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `create_template_restriction`

- **INFO** `request_parameter_mapping_missing` `product_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_type; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_group`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_group; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `create_user`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `create_virtual_card`

- **INFO** `request_parameter_mapping_missing` `contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contract_id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `template_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=template_id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `timestamp`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.number`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.carrier`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.product`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.status`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `delete_invite`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `delete_template`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `delete_template_georestriction`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `delete_template_limit`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `delete_template_restriction`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `delete_user`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `detach_card`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `detach_contracts`

- **INFO** `request_parameter_mapping_missing` `data`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=data; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `get_azs_filters`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **WARNING** `missing_response_field` `data.filter`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.items`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива items.code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива items.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)

### `get_azs_list_v1`

- **INFO** `request_parameter_mapping_missing` `q`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=q; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.total_count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].siebelId`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contractNumber`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contractName`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].status`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].countryCode`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].regionCode`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].belongsTo`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].partner`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].ownType`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].openDate`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].latitude`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].longitude`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].type`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].address`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].searchTxt`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.result[].Terminals[].id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Terminals[].active`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=bool; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Terminals[].name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Terminals[].status`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Terminals[].type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Terminals[].connectionType`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Terminals[].number`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.track_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.kmRoad`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.roadSide`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Address.city`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.street`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.house`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.building`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.phone`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].Address.fax`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].ID`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].GasStationID`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].GoodsCode`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].Price`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].Currency`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].DateTo`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].Prices[].DateFrom`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].working_time.Weekday`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].working_time.StartWorkTime`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].working_time.FinishWorkTime`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `get_azs_list_v2`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `page`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=page; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `on_page`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=on_page; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.siebel_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.status`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.full_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.brand`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.poi_type_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.poi_type_code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.own_type_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.own_type_code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.contract_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.contract_number`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.phone`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.utc_timezone`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.time_zone`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.open_date`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.close_date`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.last_update`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.height_post`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.country_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.country_code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.region_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.region_code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address_full`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.location`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.latitude`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.longitude`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.location_type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.adblue`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.electric_charging_station`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.secession_gpn`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.partner`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.belongs_to`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.info`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.search_txt`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.accept_cards`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.services_with_card`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.services_without_card`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.payment_type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.working_time`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.location.type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.location.coordinates`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.из массива payment_type.code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.из массива payment_type.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].active`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].status`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].connectionType`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.terminals[].number`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.track_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.kmRoad`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.roadSide`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.city`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.street`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.house`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.building`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.phone`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.address.fax`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].ID`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].GasStationID`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].GoodsCode`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].Price`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].Currency`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].DateTo`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].DateFrom`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].hex_color`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].CurrencyName`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].sort`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].Weekday`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].StartWorkTime`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].FinishWorkTime`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].Everyday`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.prices[].Round-The-Clock`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.services_with_card.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.services_with_card.items`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.services_without_card.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.services_without_card.items`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.adblue.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.adblue.items`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.electric_charging_station.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.массива result.electric_charging_station.items`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка services_with_card.items.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка services_with_card.items.code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка services_with_card.items.sort`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.из списка services_without_card.items.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка services_without_card.items.code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка services_without_card.items.sort`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.из списка adblue.items.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка adblue.items.code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка adblue.items.sort`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)
- **WARNING** `missing_response_field` `data.из списка electric_charging_station.items.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка electric_charging_station.items.code`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=+; actual=missing)
- **WARNING** `missing_response_field` `data.из списка electric_charging_station.items.sort`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=-; actual=missing)

### `get_card_detail`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].can_work_offline`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].card_auth_type`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_type_mismatch` `data.result[].date_last_usage`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=datetime | str | None)
- **ERROR** `response_type_mismatch` `data.result[].date_released`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=datetime | str | None)
- **WARNING** `missing_response_field` `data.result[].servicecenter_last_usage`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `response_required_mismatch` `data.result[].product`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].carrier`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].available`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].currency`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].payment_of_tolls`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.result[].mpc`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=bool; actual=missing)
- **ERROR** `missing_response_field` `data.result[].pin_reset`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)
- **ERROR** `missing_response_field` `data.result[].pin_counter`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)
- **ERROR** `response_type_mismatch` `data.result[].transaction_timeout.type`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=str | int)
- **ERROR** `response_type_mismatch` `data.result[].transaction_timeout.value`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=str | int)

### `get_card_drivers`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].role`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_card_groups`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_type_mismatch` `data.result[].cards_count`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)

### `get_card_transactions_v2`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_type_mismatch` `data.result[].id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `response_required_mismatch` `data.result[].utc_time`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].product_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_type_mismatch` `data.result[].check_id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `response_type_mismatch` `data.result[].stor_transaction_id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `missing_response_field` `data.result[].is_manual_correction`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=bool; actual=missing)
- **ERROR** `response_type_mismatch` `data.result[].qty`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].price`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].price_no_discount`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].sum`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].sum_no_discount`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].discount`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].exchange_rate`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)

### `get_cards_by_group`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].group`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].product`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].payment_of_tolls`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_cards_v1`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].can_work_offline`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].card_auth_type`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].date_expired`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **WARNING** `missing_response_field` `data.result[].servicecenter_last_usage`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `response_required_mismatch` `data.result[].product`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].payment_of_tolls`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_type_mismatch` `data.result[].transaction_timeout.type`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=str | int)
- **ERROR** `response_type_mismatch` `data.result[].transaction_timeout.value`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=str | int)

### `get_cards_v2`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_contract_data`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.template_id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.Is_dealer`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=bool; actual=missing)
- **ERROR** `response_required_mismatch` `data.managerData`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `fixture_model_validation_failed`: 5 validation errors for ContractDataResponse
data.status
  Field required [type=missing, input_value={'mpc': True, 'template_i..._phone': '79990000000'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
data.status_crm
  Field required [type=missing, input_value={'mpc': True, 'template_i..._phone': '79990000000'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
data.is_dealer
  Field required [type=missing, input_value={'mpc': True, 'template_i..._phone': '79990000000'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
data.contractData.discount_scheme
  Field required [type=missing, input_value={'contract_id': '1-7MMKF'... продажи ООО'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
data.contractData.product_type
  Field required [type=missing, input_value={'contract_id': '1-7MMKF'... продажи ООО'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing (actual=/Users/andrejraspopov/Documents/New project/api-pro-sdk/tests/fixtures/spec/1.1.60/contracts/get_contract_data.success.json)

### `get_dictionary`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.total_count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_documents`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].name_doc`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].consignee`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_final_prices`

- **INFO** `request_parameter_mapping_missing` `contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contract_id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `get_info`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.client_info.Contract`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.client_info.ContractName`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_type_mismatch` `data.client_info.Cost`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=float)
- **ERROR** `response_required_mismatch` `data.methods.all`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.methods.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)

### `get_invites`

- **INFO** `request_parameter_mapping_missing` `filter`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=filter; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].attempts`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].cards`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].initiator`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contracts`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].communication_type`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].expired_at`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].cards[].status`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].cards[].status_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].cards[].contract_id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].cards[].contract_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contracts[].status`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contracts[].status_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contracts[].cards_count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_invoices`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_type_mismatch` `data.result[].date_end`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=str)
- **ERROR** `response_type_mismatch` `data.result[].last_update`: Тип спецификации не совпадает с Python-типом модели. (expected=float; actual=str)
- **ERROR** `response_type_mismatch` `data.result[].currency`: Тип спецификации не совпадает с Python-типом модели. (expected=float; actual=str)
- **ERROR** `response_type_mismatch` `data.result[].amount`: Тип спецификации не совпадает с Python-типом модели. (expected=float; actual=str)
- **ERROR** `response_required_mismatch` `data.result[].comment`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_limits`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].productType`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].time`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].amount.used`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.result[].sum.used`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=float; actual=missing)
- **ERROR** `response_required_mismatch` `data.result[].term.type`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.result[].term.time.number`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)
- **ERROR** `missing_response_field` `data.result[].term.time.type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)
- **ERROR** `response_required_mismatch` `data.result[].transactions.count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].transactions.occured`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_payments`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_region_limits`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_report_job_list_v1`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **WARNING** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data[].date`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.data[].client_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.data[].user_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.data[].contract_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.data[].job_id`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.data[].report_name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.data[].report_format`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `get_report_jobs`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.total_count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].client_id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].user_id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contract_id`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].available_after`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_reports`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `missing_response_field` `data.result[].parameters.name`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].parameters.value`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `missing_response_field` `data.result[].parameters.label`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].parameters.default_value`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **WARNING** `missing_response_field` `data.result[].parameters.menu_values`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.result[].parameters.type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `get_restrictions`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].restriction_type`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_template_georestrictions`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].country`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].countryName`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_template_limits`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].term`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].transactions`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].time`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].productType`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].productTypeName`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].term.type`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].transactions.count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].amount.unit`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].amount.value`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].sum.currency`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].sum.value`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `missing_response_field` `data.result[].term.time.number`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)
- **ERROR** `missing_response_field` `data.result[].term.time.type`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=uint; actual=missing)

### `get_template_restrictions`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].productType`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].productTypeName`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `get_templates`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_transaction_detail`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_type_mismatch` `data.result[].id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `missing_response_field` `data.result[].date`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)
- **ERROR** `response_required_mismatch` `data.result[].utc_time`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].product_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_type_mismatch` `data.result[].check_id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `response_type_mismatch` `data.result[].stor_transaction_id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `missing_response_field` `data.result[].is_manual_correction`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=bool; actual=missing)
- **ERROR** `response_type_mismatch` `data.result[].qty`: Тип спецификации не совпадает с Python-типом модели. (expected=uint; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].price`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].price_no_discount`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].sum`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].sum_no_discount`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].discount`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)
- **ERROR** `response_type_mismatch` `data.result[].exchange_rate`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=float)

### `get_transactions_v1`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].service_center`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].transaction_items`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `get_transactions_v2`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_type_mismatch` `data.result[].id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `response_required_mismatch` `data.result[].utc_time`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].product_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_type_mismatch` `data.result[].check_id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `response_type_mismatch` `data.result[].stor_transaction_id`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=int)
- **ERROR** `missing_response_field` `data.result[].is_manual_correction`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=bool; actual=missing)

### `get_users`

- **INFO** `request_parameter_mapping_missing` `contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contract_id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.result`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].middle_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].date`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].position`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].active`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.result[].cards[].product`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].cards[].contract_name`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_type_mismatch` `data.result[].cards[].available`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=bool)
- **ERROR** `response_type_mismatch` `data.result[].contracts[].available`: Тип спецификации не совпадает с Python-типом модели. (expected=string; actual=bool)
- **ERROR** `response_required_mismatch` `data.result[].contracts[].status`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.result[].contracts[].cards_count`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `logoff`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `move_to_card`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `move_to_contract`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `order_cards`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `order_documents_email`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `format`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=format; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `order_invoice`

- **INFO** `request_parameter_mapping_missing` `sum`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `order_report`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.job_id`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `order_report_v1`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=[string]; actual=missing)

### `prolong_invite`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `release_virtual_card`

- **INFO** `request_parameter_mapping_missing` `contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contract_id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `timestamp`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.number`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.carrier`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.product`: Обязательность поля отличается от спецификации. (expected=False; actual=True)
- **ERROR** `response_required_mismatch` `data.status`: Обязательность поля отличается от спецификации. (expected=False; actual=True)

### `remove_card_group`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `remove_limit`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `remove_region_limit`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `remove_restriction`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `repository`

- **INFO** `sdk_untyped_model_field` `api_client_opti24.models.reports.ReportOrderParams.additional`: Pydantic-модель содержит Any или dict с Any. (actual=dict[str, Any] | None)
- **INFO** `sdk_untyped_model_field` `api_client_opti24.models.reports.ReportParameter.value`: Pydantic-модель содержит Any или dict с Any. (actual=Any | None)

### `resend_invite`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `response_required_mismatch` `data.attempts`: Обязательность поля отличается от спецификации. (expected=True; actual=False)
- **ERROR** `response_required_mismatch` `data.expired_at`: Обязательность поля отличается от спецификации. (expected=True; actual=False)

### `reset_pin`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `set_card_comment`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `set_card_group`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `set_card_product`

- **INFO** `request_parameter_mapping_missing` `card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=card_id; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **WARNING** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=[string, string]; actual=missing)

### `set_cards_to_group`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)

### `set_limit`

- **INFO** `request_parameter_mapping_missing` `limit`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].group_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].productGroup`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].productType`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].amount`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].sum`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].term`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].time`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].transactions`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].amount.unit`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].amount.value`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].sum.currency`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].sum.value`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].term.days`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].term.time`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].term.type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.time.from`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.time.to`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].term.time.number`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].term.time.type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `limit[].transactions.count`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=limit; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=[string]; actual=missing)

### `set_region_limit`

- **INFO** `request_parameter_mapping_missing` `region_limit`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=region_limit; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.group_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.country`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.region`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.service_center`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.partner`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction.limit_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **WARNING** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=[string]; actual=missing)

### `set_restriction`

- **INFO** `request_parameter_mapping_missing` `restriction`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].group_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].productGroup`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].productType`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=[string]; actual=missing)

### `update_template`

- **INFO** `request_parameter_mapping_missing` `type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `update_template_georestriction`

- **INFO** `request_parameter_mapping_missing` `country`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=country; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `region`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=region; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `partner`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=partner; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `service_center`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=service_center; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `update_template_limit`

- **INFO** `request_parameter_mapping_missing` `amount`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=amount; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `sum`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `time`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=time; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_type; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_group`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_group; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `amount.unit`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=amount; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `amount.value`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=amount; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `sum.currency`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `sum.value`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `time.number`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=time; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `time.type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=time; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.days`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.time`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `term.type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=term; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `update_template_restriction`

- **INFO** `request_parameter_mapping_missing` `product_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_type; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_group`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_group; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)
- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
- **ERROR** `missing_response_field` `data.data`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=string; actual=missing)

### `verify_pin`

- **WARNING** `missing_response_field` `status.errors`: Поле спецификации отсутствует в Pydantic-модели ответа. (expected=json; actual=missing)
