# Domain context

Cascade Cycles Group sells bicycles and components through dealers, rental fleets,
schools and clubs. Salesforce is the system of record for deals; there is no CRM
replacement planned.

## What lives here

Nothing yet. This repo is the starting point for building the warehouse side of
revenue reporting, and its history begins with the requirement in `docs/`.

## Conventions

- Warehouse target is DuckDB for development.
- Source-aligned models are named `stg_<source>__<object>`; marts are `fct_*` or
  `dim_*`.
- A figure that cannot be attributed is reported, never dropped — if revenue
  cannot reach a product family it is shown as its own number.
- Where the business has more than one candidate field for a definition, the
  choice is recorded in the repository next to the model, with the numbers each
  candidate produced.
- Every documented data condition gets a test, not a comment.

## Source systems

| System | Objects in play | Notes |
| --- | --- | --- |
| Salesforce | Opportunity, OpportunityLineItem, Product | Read-only; credentials resolve from the domain secret store at run time and are never held in the repo. See `seed/salesforce.sql` for the development fixture |

## Who consumes this

Sales Operations owns revenue reporting. Finance consumes it at the monthly close
— the two currently disagree, which is the problem this work exists to settle. The
executive dashboard reads the same models rather than its own copy.
