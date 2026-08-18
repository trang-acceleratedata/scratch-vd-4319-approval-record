# REV-2026-014 — Monthly Revenue Reporting Requirement

| Field | Value |
| --- | --- |
| Document ID | REV-2026-014 |
| Version | 1.3 |
| Status | Approved for build |
| Owner | Revenue Operations |
| Last revised | 11 August 2026 |

## 1. Background

Sales Operations reports monthly revenue from Salesforce by hand, exporting
Opportunity data to a spreadsheet each month. The figure is reconciled late, is
not reproducible, and has twice disagreed with the number Finance presented at
the monthly close. We want the same figure produced from the warehouse, on a
schedule, with tests.

## 2. Scope

Monthly recognised revenue by customer account, sourced from Salesforce
Opportunity data, for the trailing 24 months.

In scope:

- Opportunity and OpportunityLineItem
- Account, for the customer dimension and its parent/child hierarchy
- Currency conversion to the reporting currency

Out of scope:

- Forecast or pipeline revenue
- Subscription/recurring revenue schedules
- Product-level revenue detail
- Anything sourced outside Salesforce

## 3. Definitions

**Recognised revenue.** The Amount on an Opportunity whose StageName is
`Closed Won`, attributed to the calendar month of its CloseDate.

**Reporting currency.** USD. Opportunity records carry `CurrencyIsoCode` and
`ConversionRate`; the converted amount is `Amount * ConversionRate`.

**Account hierarchy.** Some accounts are subsidiaries and carry `ParentId`.
Revenue Operations reports at the individual account level today.

## 4. Known data conditions

These are present in the source and have caused disagreement before. The build
should make its handling of each one explicit and tested.

1. **Amended deals.** An Opportunity can be closed won, then have its Amount
   revised in a later period. `LastModifiedDate` moves; `CloseDate` does not.
   Restatements have moved a closed month's total after it was reported.
2. **Orphaned line items.** A small number of OpportunityLineItem rows reference
   an OpportunityId that is absent from the Opportunity extract.
3. **Missing close dates.** A handful of closed-won Opportunities have a null
   CloseDate and therefore no month to attribute to.
4. **Multi-currency.** Roughly a fifth of opportunities are booked in a currency
   other than USD, and two carry a null ConversionRate.
5. **Test accounts.** Internal accounts used for training are flagged by name
   and should not reach the reported figure.

## 5. Consumers and cadence

- Sales Operations owns the number.
- Finance consumes it in the monthly close pack.
- The executive dashboard reads the same model.

Refresh nightly. Month-to-date should be current as of the previous business
day; a closed month should be final by the third business day of the following
month.

## 6. Success criteria

- The monthly figure is reproducible from the warehouse without manual steps.
- Each condition in section 4 has a documented decision and a test.
- Finance and Sales Operations reconcile to the same number for the trailing
  three closed months.

## Appendix A — Field reference

| Object | Field | Notes |
| --- | --- | --- |
| Opportunity | Id, AccountId, Amount, CurrencyIsoCode, ConversionRate | |
| Opportunity | StageName | `Closed Won` is the recognised set |
| Opportunity | CloseDate | Attribution month; nullable in practice |
| Opportunity | LastModifiedDate | Moves on amendment |
| OpportunityLineItem | Id, OpportunityId, ProductName, Quantity, UnitPrice | |
| Account | Id, Name, ParentId, Industry, BillingCountry | |

## Sign-off

| Role | Name | Date |
| --- | --- | --- |
| Requested by | VP, Revenue Operations | 11 August 2026 |
| Business sponsor | Chief Financial Officer | 11 August 2026 |
| Data owner | Head of Sales Systems | 10 August 2026 |
