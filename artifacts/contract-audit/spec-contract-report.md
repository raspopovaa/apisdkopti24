# API 1.1.60 contract audit

## Summary

| Metric | Value |
|---|---:|
| operations | 82 |
| verified_operations | 3 |
| fixtures | 79 |
| issues | 125 |
| blocking_issues | 0 |
| errors | 0 |
| warnings | 0 |
| info | 125 |

## Findings by code

| Code | Count |
|---|---:|
| `request_parameter_mapping_missing` | 125 |

## Details

### `attach_contracts`

- **INFO** `request_parameter_mapping_missing` `sid`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sid; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `template_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=template_id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `use_mpc`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=use_mpc; actual=not exposed by the same name)

### `auth_user`

- **INFO** `request_parameter_mapping_missing` `login`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=login; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `password`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=password; actual=not exposed by the same name)

### `block_card`

- **INFO** `request_parameter_mapping_missing` `card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=card_id; actual=not exposed by the same name)

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

### `create_template`

- **INFO** `request_parameter_mapping_missing` `type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=type; actual=not exposed by the same name)

### `create_template_georestriction`

- **INFO** `request_parameter_mapping_missing` `country`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=country; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `region`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=region; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `partner`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=partner; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `service_center`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=service_center; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)

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

### `create_template_restriction`

- **INFO** `request_parameter_mapping_missing` `product_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_type; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_group`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_group; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)

### `create_virtual_card`

- **INFO** `request_parameter_mapping_missing` `template_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=template_id; actual=not exposed by the same name)

### `detach_contracts`

- **INFO** `request_parameter_mapping_missing` `data`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=data; actual=not exposed by the same name)

### `get_azs_list_v1`

- **INFO** `request_parameter_mapping_missing` `q`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=q; actual=not exposed by the same name)

### `get_azs_list_v2`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `page`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=page; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `on_page`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=on_page; actual=not exposed by the same name)

### `get_invites`

- **INFO** `request_parameter_mapping_missing` `filter`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=filter; actual=not exposed by the same name)

### `order_documents_email`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `format`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=format; actual=not exposed by the same name)

### `order_invoice`

- **INFO** `request_parameter_mapping_missing` `sum`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=sum; actual=not exposed by the same name)

### `order_report`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)

### `release_virtual_card`

- **INFO** `request_parameter_mapping_missing` `contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=contract_id; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=type; actual=not exposed by the same name)

### `set_card_group`

- **INFO** `request_parameter_mapping_missing` `id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=id; actual=not exposed by the same name)

### `set_card_product`

- **INFO** `request_parameter_mapping_missing` `card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=card_id; actual=not exposed by the same name)

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

### `set_restriction`

- **INFO** `request_parameter_mapping_missing` `restriction`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].card_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].group_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].contract_id`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].productGroup`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].productType`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction[].restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction; actual=not exposed by the same name)

### `update_template`

- **INFO** `request_parameter_mapping_missing` `type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=type; actual=not exposed by the same name)

### `update_template_georestriction`

- **INFO** `request_parameter_mapping_missing` `country`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=country; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `region`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=region; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `partner`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=partner; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `service_center`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=service_center; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)

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

### `update_template_restriction`

- **INFO** `request_parameter_mapping_missing` `product_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_type; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `product_group`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=product_group; actual=not exposed by the same name)
- **INFO** `request_parameter_mapping_missing` `restriction_type`: Параметр API не представлен одноимённым аргументом SDK; требуется явное сопоставление. (expected=restriction_type; actual=not exposed by the same name)
