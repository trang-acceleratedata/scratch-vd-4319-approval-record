# Domain context

Sales and revenue reporting for a mid-market B2B business. Salesforce is the
system of record for customers and deals; there is no CRM replacement planned.

## What lives here

Nothing yet. This repo is the starting point for building the warehouse side of
revenue reporting, and its history begins with the requirement in `docs/`.

## Conventions

- Warehouse target is DuckDB for development.
- Source-aligned models are named `stg_<source>__<object>`; marts are named
  `fct_*` or `dim_*`.
- Money is stored in the reporting currency (USD) with the original currency and
  rate retained alongside it, so a figure can always be explained.
- Every documented data condition gets a test, not a comment.

## Source systems

| System | Objects in play | Notes |
| --- | --- | --- |
| Salesforce | Account, Opportunity, OpportunityLineItem | Extracted to the warehouse; see `seed/salesforce.sql` for the development fixture |

## Who consumes this

Sales Operations owns revenue reporting. Finance consumes it in the monthly
close. The executive dashboard reads the same models rather than its own copy.
