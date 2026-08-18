# CASCADE CYCLES GROUP

## REV-2026-014 — Monthly Revenue Reporting

| Field | Value |
| --- | --- |
| Document ID | REV-2026-014 |
| Version | 1.0 |
| Status | Approved for build |
| Owner | Revenue Operations |
| Date | 11 August 2026 |

## 1. Background

Monthly revenue is assembled by hand from a Salesforce export. It takes two days,
it is not reproducible, and it has twice disagreed with the figure Finance
presented at the monthly close. The disagreement in Appendix A has been open
since June and nobody can currently say which number is right.

## 2. Business objective

One automated, repeatable pipeline that lands Salesforce deal data in our data
platform, and one governed reporting model on top of it that gives monthly
revenue by product family — with the definition of "closed-won revenue" written
down, agreed, and traceable back to whoever agreed it.

## 3. Business questions this must answer

- What was closed-won revenue by month, for the last 24 months?
- How does each product family contribute to that, month by month?
- How much revenue cannot be attributed to a product family at all?
- Which definition of "closed won" produced the number being read?

## 4. Scope

**IN SCOPE**

- Loading Salesforce opportunities, opportunity line items, and products into our
  data platform.
- A transformation layer that produces the monthly revenue reporting model.
- Tests and documentation for both.

**OUT OF SCOPE**

- Any other Salesforce object — accounts, contacts, leads, campaigns, activities.
  We want these later; not in this piece of work.
- Dashboards, report front-ends and BI tool configuration.
- Writing anything back into Salesforce.
- Forecast or open-pipeline reporting.

## 5. Requirements

### R1 — Getting the data in

| ID | Requirement |
| --- | --- |
| R1.1 | Deal data must load from Salesforce into our data platform automatically. No manual export step. |
| R1.2 | Opportunities, opportunity line items and products must all be available. |
| R1.3 | The load must be repeatable. Running it twice must not duplicate or double-count rows. |
| R1.4 | The landed data must stay faithful to the source. No filtering, renaming or business logic at this stage. |
| R1.5 | It must be possible to tell which load a given row arrived in, and when that load ran. |
| R1.6 | No Salesforce credential may be stored in the repository. |

### R2 — Turning it into a reporting model

| ID | Requirement |
| --- | --- |
| R2.1 | A reporting model must give closed-won revenue by calendar month and by product family. |
| R2.2 | The month must be derived from the deal's close date. |
| R2.3 | Product family must come from the product record, not from free text typed on the deal. |
| R2.4 | The model must carry both a revenue amount and a count of deals. |
| R2.5 | The model must state, in writing, which definition of "closed won" it uses and which revenue figure it sums. |
| R2.6 | Revenue that cannot be attributed to a product family must be visible as its own figure, not silently dropped. |
| R2.7 | Key columns must be tested for uniqueness and completeness. |

### R3 — Making it defensible

| ID | Requirement |
| --- | --- |
| R3.1 | The agreed definitions must be recorded in the repository alongside the model — not in email, not in chat. |
| R3.2 | Any later change to a definition must be reviewable: who decided, when, and why. |
| R3.3 | The build must be reproducible by someone who did not write it. |

## 6. Definitions, as the business states them today

| Term | What the business means by it |
| --- | --- |
| Closed-won revenue | Revenue from deals we have won |
| Revenue | The value of the deal |
| Product family | The family of bike or part the revenue belongs to |
| Month | The month the deal closed |

These are the definitions in use today, and they are as precise as the business
can currently be. Where Salesforce offers more than one field that could satisfy
one of them, the delivery team must bring the options back to the requester, with
the numbers each one produces, and let the requester choose.

## 7. Acceptance criteria

| ID | Criterion |
| --- | --- |
| A1 | The three Salesforce objects land in the data platform and can be queried. |
| A2 | Rerunning the load leaves row counts stable. |
| A3 | A monthly revenue by product family result set is produced, covering all nine families. |
| A4 | The closed-won definition and the revenue definition each appear in a file in the repository, with a date and an approval against them. |
| A5 | Unattributed revenue is reported as its own visible figure. |
| A6 | Tests exist for the model's keys and they pass. |
| A7 | The requester can see how each number was verified, without reading the code. |

## 8. Assumptions

- Salesforce remains the system of record for deal data throughout.
- The nine product families in Appendix C are complete and stable for this
  reporting period.
- Currency is single-currency USD. Multi-currency is a later requirement.
- The data platform for this domain is already provisioned and active.

## 9. Constraints and dependencies

- Access to the Salesforce instance is read only, via an existing session token.
  There is no login flow available to this project.
- Credential values are provisioned into the domain's secret store by the
  platform team. Allow two working days' lead time. The delivery team never holds
  them in the repository.
- The source instance does not answer aggregate queries. All aggregation happens
  after the data has landed.

## Appendix A — The reporting discrepancy we need settled

Both figures below were produced from the same Salesforce org, on the same day, by
people who each believe their number is correct.

| Report | Deals | Total value |
| --- | --- | --- |
| Sales Ops — deals at stage "Closed Won" | 3,794 | $1,418,099,415 |
| Finance — won-deal extract | 2,961 | $1,105,896,542 |
| Difference | 833 | $312,202,874 |

The gap is 22% of the larger figure. Deciding which of the two this project
reports is part of the work, and the answer must be recorded where the next
person can find it.

## Appendix B — Source system access

Read-only access is provided through an existing session token held in the
domain's secret store. The delivery team resolves it at run time and never copies
it into the repository or into any document.

| Property | Value |
| --- | --- |
| Instance endpoint | Provisioned per environment; resolved from the secret store |
| Credential | Session token, secret-store reference only — never a literal |
| Aggregate queries | Not supported by the source instance |
| Row volumes | Opportunities and line items in the low tens of thousands |

## Appendix C — What the July discovery spike found

| Finding | Figure |
| --- | --- |
| Opportunities at "Closed Won" with no line items at all | 8% |
| Line items whose product cannot be resolved to a family | 22% |
| Line items where Quantity × UnitPrice does not equal TotalPrice | Present, unquantified |
| Distinct product families in the product record | 9 |

The spike also found that `StageName = "Closed Won"` and the `IsWon` flag do not
always agree, which is the most likely source of the Appendix A gap.

## Sign-off

| Role | Name | Date |
| --- | --- | --- |
| Requested by | VP, Revenue Operations | 11 August 2026 |
| Business sponsor | Chief Financial Officer | 11 August 2026 |
