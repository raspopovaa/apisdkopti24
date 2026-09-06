# Типы данных

Типизированные Pydantic-модели запросов и ответов SDK. Для каждой модели показаны типы после валидации, JSON-типы, обязательность, nullable, значения по умолчанию, ограничения схемы и пользовательские валидаторы.

## `auth`

- [`AccessRights`](auth/AccessRights.md)
- [`AuthError`](auth/AuthError.md)
- [`AuthErrorResponse`](auth/AuthErrorResponse.md)
- [`AuthUserData`](auth/AuthUserData.md)
- [`AuthUserResponse`](auth/AuthUserResponse.md)
- [`ClientInfo`](auth/ClientInfo.md)
- [`ContractInfo`](auth/ContractInfo.md)
- [`GetInfoResponse`](auth/GetInfoResponse.md)
- [`InfoData`](auth/InfoData.md)
- [`LogoffResponse`](auth/LogoffResponse.md)
- [`MethodsCount`](auth/MethodsCount.md)
- [`MethodsInfo`](auth/MethodsInfo.md)
- [`StatusResponse`](auth/StatusResponse.md)

## `card_group`

- [`CardGroupAssignmentRequest`](card_group/CardGroupAssignmentRequest.md)
- [`CardGroupItem`](card_group/CardGroupItem.md)
- [`CardGroupListData`](card_group/CardGroupListData.md)
- [`CardGroupListResponse`](card_group/CardGroupListResponse.md)
- [`RemoveCardGroupResponse`](card_group/RemoveCardGroupResponse.md)
- [`SetCardGroupData`](card_group/SetCardGroupData.md)
- [`SetCardGroupResponse`](card_group/SetCardGroupResponse.md)
- [`SetCardsToGroupResponse`](card_group/SetCardsToGroupResponse.md)

## `cards`

- [`BoolResponse`](cards/BoolResponse.md)
- [`CardDetail`](cards/CardDetail.md)
- [`CardDetailData`](cards/CardDetailData.md)
- [`CardDetailResponse`](cards/CardDetailResponse.md)
- [`CardDriverInfo`](cards/CardDriverInfo.md)
- [`CardDriversData`](cards/CardDriversData.md)
- [`CardDriversResponse`](cards/CardDriversResponse.md)
- [`CardGroupData`](cards/CardGroupData.md)
- [`CardGroupInfo`](cards/CardGroupInfo.md)
- [`CardGroupResponse`](cards/CardGroupResponse.md)
- [`CardInfo`](cards/CardInfo.md)
- [`CardV2Item`](cards/CardV2Item.md)
- [`CardsListData`](cards/CardsListData.md)
- [`CardsListResponse`](cards/CardsListResponse.md)
- [`CardsV2Data`](cards/CardsV2Data.md)
- [`CardsV2Response`](cards/CardsV2Response.md)
- [`IDListResponse`](cards/IDListResponse.md)
- [`TransactionTimeout`](cards/TransactionTimeout.md)

## `contracts`

- [`BalanceData`](contracts/BalanceData.md)
- [`CardsData`](contracts/CardsData.md)
- [`ContractData`](contracts/ContractData.md)
- [`ContractDataResponse`](contracts/ContractDataResponse.md)
- [`ContractResponse`](contracts/ContractResponse.md)
- [`DocumentItem`](contracts/DocumentItem.md)
- [`DocumentsData`](contracts/DocumentsData.md)
- [`DocumentsOrderResponse`](contracts/DocumentsOrderResponse.md)
- [`DocumentsResponse`](contracts/DocumentsResponse.md)
- [`InvoiceItem`](contracts/InvoiceItem.md)
- [`InvoiceOrderResponse`](contracts/InvoiceOrderResponse.md)
- [`InvoicesData`](contracts/InvoicesData.md)
- [`InvoicesResponse`](contracts/InvoicesResponse.md)
- [`ManagerData`](contracts/ManagerData.md)
- [`OrderCardsResponse`](contracts/OrderCardsResponse.md)
- [`PaymentItem`](contracts/PaymentItem.md)
- [`PaymentsData`](contracts/PaymentsData.md)
- [`PaymentsResponse`](contracts/PaymentsResponse.md)

## `dictionaries`

- [`AddressV1`](dictionaries/AddressV1.md)
- [`AddressV2`](dictionaries/AddressV2.md)
- [`AzsFilterItem`](dictionaries/AzsFilterItem.md)
- [`AzsFilterValue`](dictionaries/AzsFilterValue.md)
- [`AzsFiltersResponse`](dictionaries/AzsFiltersResponse.md)
- [`AzsItemV1`](dictionaries/AzsItemV1.md)
- [`AzsItemV2`](dictionaries/AzsItemV2.md)
- [`AzsListV1Data`](dictionaries/AzsListV1Data.md)
- [`AzsListV1Response`](dictionaries/AzsListV1Response.md)
- [`AzsListV2Data`](dictionaries/AzsListV2Data.md)
- [`AzsListV2Response`](dictionaries/AzsListV2Response.md)
- [`Coordinates`](dictionaries/Coordinates.md)
- [`DictionaryData`](dictionaries/DictionaryData.md)
- [`DictionaryItem`](dictionaries/DictionaryItem.md)
- [`DictionaryResponse`](dictionaries/DictionaryResponse.md)
- [`PriceItemV1`](dictionaries/PriceItemV1.md)
- [`PriceItemV2`](dictionaries/PriceItemV2.md)
- [`ServiceGroup`](dictionaries/ServiceGroup.md)
- [`ServiceItem`](dictionaries/ServiceItem.md)
- [`TerminalV1`](dictionaries/TerminalV1.md)
- [`TerminalV2`](dictionaries/TerminalV2.md)
- [`WorkingTimeV1`](dictionaries/WorkingTimeV1.md)
- [`WorkingTimeV2`](dictionaries/WorkingTimeV2.md)

## `ewallet`

- [`MoveToCardResponse`](ewallet/MoveToCardResponse.md)
- [`MoveToContractResponse`](ewallet/MoveToContractResponse.md)
- [`SetCardProductResponse`](ewallet/SetCardProductResponse.md)

## `final_prices`

- [`CheckPurchaseRequest`](final_prices/CheckPurchaseRequest.md)
- [`CheckPurchaseResponse`](final_prices/CheckPurchaseResponse.md)
- [`FinalPriceItem`](final_prices/FinalPriceItem.md)
- [`FinalPricesData`](final_prices/FinalPricesData.md)
- [`FinalPricesResponse`](final_prices/FinalPricesResponse.md)
- [`PurchaseGoodItem`](final_prices/PurchaseGoodItem.md)

## `invites`

- [`InviteActionResult`](invites/InviteActionResult.md)
- [`InviteBoolResponse`](invites/InviteBoolResponse.md)
- [`InviteCard`](invites/InviteCard.md)
- [`InviteContract`](invites/InviteContract.md)
- [`InviteCreateRequest`](invites/InviteCreateRequest.md)
- [`InviteItem`](invites/InviteItem.md)
- [`InviteList`](invites/InviteList.md)
- [`InviteListResponse`](invites/InviteListResponse.md)
- [`InviteResponse`](invites/InviteResponse.md)
- [`_InviteContractRequest`](invites/_InviteContractRequest.md)

## `limits`

- [`LimitAmount`](limits/LimitAmount.md)
- [`LimitAmountRequest`](limits/LimitAmountRequest.md)
- [`LimitItem`](limits/LimitItem.md)
- [`LimitRequestItem`](limits/LimitRequestItem.md)
- [`LimitSum`](limits/LimitSum.md)
- [`LimitSumRequest`](limits/LimitSumRequest.md)
- [`LimitTerm`](limits/LimitTerm.md)
- [`LimitTermRequest`](limits/LimitTermRequest.md)
- [`LimitTermTime`](limits/LimitTermTime.md)
- [`LimitTermTimeRequest`](limits/LimitTermTimeRequest.md)
- [`LimitTime`](limits/LimitTime.md)
- [`LimitTimeRequest`](limits/LimitTimeRequest.md)
- [`LimitTransactions`](limits/LimitTransactions.md)
- [`LimitTransactionsRequest`](limits/LimitTransactionsRequest.md)
- [`LimitsData`](limits/LimitsData.md)
- [`LimitsResponse`](limits/LimitsResponse.md)
- [`RemoveLimitResponse`](limits/RemoveLimitResponse.md)
- [`SetLimitResponse`](limits/SetLimitResponse.md)

## `modeling`

- [`ResponseStatus`](modeling/ResponseStatus.md)

## `region_limits`

- [`RegionLimit`](region_limits/RegionLimit.md)
- [`RegionLimitList`](region_limits/RegionLimitList.md)
- [`RegionLimitRequestItem`](region_limits/RegionLimitRequestItem.md)
- [`RegionLimitResponse`](region_limits/RegionLimitResponse.md)
- [`RegionLimitSetResponse`](region_limits/RegionLimitSetResponse.md)
- [`RemoveRegionLimit`](region_limits/RemoveRegionLimit.md)

## `reports`

- [`ReportFileResponse`](reports/ReportFileResponse.md)
- [`ReportItem`](reports/ReportItem.md)
- [`ReportJobItem`](reports/ReportJobItem.md)
- [`ReportJobList`](reports/ReportJobList.md)
- [`ReportJobListResponse`](reports/ReportJobListResponse.md)
- [`ReportList`](reports/ReportList.md)
- [`ReportListResponse`](reports/ReportListResponse.md)
- [`ReportOrderData`](reports/ReportOrderData.md)
- [`ReportOrderParams`](reports/ReportOrderParams.md)
- [`ReportOrderRequest`](reports/ReportOrderRequest.md)
- [`ReportOrderResponse`](reports/ReportOrderResponse.md)
- [`ReportParameter`](reports/ReportParameter.md)
- [`ReportParameterMenuValue`](reports/ReportParameterMenuValue.md)
- [`ReportV1JobItem`](reports/ReportV1JobItem.md)
- [`ReportV1JobListResponse`](reports/ReportV1JobListResponse.md)
- [`ReportV1OrderResponse`](reports/ReportV1OrderResponse.md)

## `request_parts`

- [`ContractForm`](request_parts/ContractForm.md)
- [`ContractQuery`](request_parts/ContractQuery.md)
- [`DateRangePaginationQuery`](request_parts/DateRangePaginationQuery.md)

## `restrictions`

- [`RestrictionGetResponse`](restrictions/RestrictionGetResponse.md)
- [`RestrictionItem`](restrictions/RestrictionItem.md)
- [`RestrictionList`](restrictions/RestrictionList.md)
- [`RestrictionRemoveResponse`](restrictions/RestrictionRemoveResponse.md)
- [`RestrictionRequestItem`](restrictions/RestrictionRequestItem.md)
- [`RestrictionSetResponse`](restrictions/RestrictionSetResponse.md)

## `templates`

- [`LimitAmount`](templates/LimitAmount.md)
- [`LimitSum`](templates/LimitSum.md)
- [`LimitTerm`](templates/LimitTerm.md)
- [`LimitTermTime`](templates/LimitTermTime.md)
- [`LimitTime`](templates/LimitTime.md)
- [`LimitTransactions`](templates/LimitTransactions.md)
- [`TemplateCreateRequest`](templates/TemplateCreateRequest.md)
- [`TemplateCreateResponse`](templates/TemplateCreateResponse.md)
- [`TemplateDeleteResponse`](templates/TemplateDeleteResponse.md)
- [`TemplateGeoRestriction`](templates/TemplateGeoRestriction.md)
- [`TemplateGeoRestrictionCreateRequest`](templates/TemplateGeoRestrictionCreateRequest.md)
- [`TemplateGeoRestrictionCreateResponse`](templates/TemplateGeoRestrictionCreateResponse.md)
- [`TemplateGeoRestrictionDeleteResponse`](templates/TemplateGeoRestrictionDeleteResponse.md)
- [`TemplateGeoRestrictionListData`](templates/TemplateGeoRestrictionListData.md)
- [`TemplateGeoRestrictionListResponse`](templates/TemplateGeoRestrictionListResponse.md)
- [`TemplateItem`](templates/TemplateItem.md)
- [`TemplateLimit`](templates/TemplateLimit.md)
- [`TemplateLimitCreateRequest`](templates/TemplateLimitCreateRequest.md)
- [`TemplateLimitCreateResponse`](templates/TemplateLimitCreateResponse.md)
- [`TemplateLimitDeleteResponse`](templates/TemplateLimitDeleteResponse.md)
- [`TemplateLimitListData`](templates/TemplateLimitListData.md)
- [`TemplateLimitListResponse`](templates/TemplateLimitListResponse.md)
- [`TemplateRestriction`](templates/TemplateRestriction.md)
- [`TemplateRestrictionCreateRequest`](templates/TemplateRestrictionCreateRequest.md)
- [`TemplateRestrictionCreateResponse`](templates/TemplateRestrictionCreateResponse.md)
- [`TemplateRestrictionDeleteResponse`](templates/TemplateRestrictionDeleteResponse.md)
- [`TemplateRestrictionListData`](templates/TemplateRestrictionListData.md)
- [`TemplateRestrictionListResponse`](templates/TemplateRestrictionListResponse.md)
- [`TemplatesListData`](templates/TemplatesListData.md)
- [`TemplatesListResponse`](templates/TemplatesListResponse.md)

## `transactions`

- [`RequestInfo`](transactions/RequestInfo.md)
- [`TransactionDetailResponse`](transactions/TransactionDetailResponse.md)
- [`TransactionItem`](transactions/TransactionItem.md)
- [`TransactionItemV2`](transactions/TransactionItemV2.md)
- [`TransactionV1`](transactions/TransactionV1.md)
- [`TransactionsV1Data`](transactions/TransactionsV1Data.md)
- [`TransactionsV1Response`](transactions/TransactionsV1Response.md)
- [`TransactionsV2Data`](transactions/TransactionsV2Data.md)
- [`TransactionsV2Response`](transactions/TransactionsV2Response.md)

## `users`

- [`UserAccess`](users/UserAccess.md)
- [`UserAttachContractRequest`](users/UserAttachContractRequest.md)
- [`UserBoolResponse`](users/UserBoolResponse.md)
- [`UserCardItem`](users/UserCardItem.md)
- [`UserContractItem`](users/UserContractItem.md)
- [`UserCreateResponse`](users/UserCreateResponse.md)
- [`UserItem`](users/UserItem.md)
- [`UserList`](users/UserList.md)
- [`UserListResponse`](users/UserListResponse.md)
- [`UserRole`](users/UserRole.md)
- [`UserStatus`](users/UserStatus.md)

## `virtual_cards`

- [`ConfirmVirtualCardRequest`](virtual_cards/ConfirmVirtualCardRequest.md)
- [`ConfirmVirtualCardResponse`](virtual_cards/ConfirmVirtualCardResponse.md)
- [`DeleteMPCResponse`](virtual_cards/DeleteMPCResponse.md)
- [`DeleteVirtualCardResponse`](virtual_cards/DeleteVirtualCardResponse.md)
- [`MPCActionResponse`](virtual_cards/MPCActionResponse.md)
- [`MPCItem`](virtual_cards/MPCItem.md)
- [`MPCListData`](virtual_cards/MPCListData.md)
- [`MPCListResponse`](virtual_cards/MPCListResponse.md)
- [`PaymentQRData`](virtual_cards/PaymentQRData.md)
- [`PaymentQRResponse`](virtual_cards/PaymentQRResponse.md)
- [`RerunVirtualCardReleaseRequest`](virtual_cards/RerunVirtualCardReleaseRequest.md)
- [`RerunVirtualCardReleaseResponse`](virtual_cards/RerunVirtualCardReleaseResponse.md)
- [`ResendSMSRequest`](virtual_cards/ResendSMSRequest.md)
- [`ResendSMSResponse`](virtual_cards/ResendSMSResponse.md)
- [`ResetMPCRequest`](virtual_cards/ResetMPCRequest.md)
- [`ResetMPCResponse`](virtual_cards/ResetMPCResponse.md)
- [`SimpleActionResponse`](virtual_cards/SimpleActionResponse.md)
- [`StatusModel`](virtual_cards/StatusModel.md)
- [`VirtualCardData`](virtual_cards/VirtualCardData.md)
- [`VirtualCardResponse`](virtual_cards/VirtualCardResponse.md)
