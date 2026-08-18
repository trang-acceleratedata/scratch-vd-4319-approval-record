-- Salesforce-shaped fixture for the VD-4319 approval-record runbook.
--
-- Every condition listed in section 4 of REV-2026-014 is physically present here,
-- so the interview's decision branches have something real behind them and
-- `identifying-data-slice` has data to profile. Without that, a run captures an
-- intent about data that does not exist and the interview is theatre.
--
-- Deliberately small (24 opportunities) — the point is coverage of the awkward
-- cases, not volume.

DROP TABLE IF EXISTS opportunity_line_item;
DROP TABLE IF EXISTS opportunity;
DROP TABLE IF EXISTS account;

CREATE TABLE account (
  id              VARCHAR PRIMARY KEY,
  name            VARCHAR NOT NULL,
  parent_id       VARCHAR,
  industry        VARCHAR,
  billing_country VARCHAR
);

CREATE TABLE opportunity (
  id                 VARCHAR PRIMARY KEY,
  account_id         VARCHAR,
  name               VARCHAR,
  stage_name         VARCHAR NOT NULL,
  amount             DECIMAL(18, 2),
  currency_iso_code  VARCHAR,
  conversion_rate    DECIMAL(12, 6),
  close_date         DATE,
  created_date       TIMESTAMP,
  last_modified_date TIMESTAMP
);

CREATE TABLE opportunity_line_item (
  id             VARCHAR PRIMARY KEY,
  opportunity_id VARCHAR NOT NULL,
  product_name   VARCHAR,
  quantity       INTEGER,
  unit_price     DECIMAL(18, 2)
);

-- Accounts. ACC-006 is a subsidiary of ACC-002 (hierarchy branch); ACC-009 is an
-- internal training account (the "test accounts" condition).
INSERT INTO account VALUES
  ('ACC-001', 'Northwind Trading',        NULL,      'Retail',        'US'),
  ('ACC-002', 'Initech Group',            NULL,      'Technology',    'US'),
  ('ACC-003', 'Umbra Logistics',          NULL,      'Logistics',     'DE'),
  ('ACC-004', 'Kessler Health',           NULL,      'Healthcare',    'US'),
  ('ACC-005', 'Ravenna Foods',            NULL,      'Manufacturing', 'IT'),
  ('ACC-006', 'Initech Labs',             'ACC-002', 'Technology',    'US'),
  ('ACC-007', 'Halberd Financial',        NULL,      'Financial',     'GB'),
  ('ACC-008', 'Solstice Media',           NULL,      'Media',         'US'),
  ('ACC-009', 'ZZ Internal Test Account', NULL,      'Internal',      'US');

-- Opportunities.
--   OPP-020        closed won, then amended later     (restatement condition)
--   OPP-021/022    closed won with a NULL close_date  (missing attribution month)
--   OPP-023        booked in EUR with NULL rate       (unconvertible)
--   OPP-024        internal test account              (must not reach the figure)
--   Closed Lost / Negotiation rows exist so "Closed Won only" is a real filter.
INSERT INTO opportunity VALUES
  ('OPP-001','ACC-001','Northwind Q2 renewal',     'Closed Won',  48000.00,'USD',1.000000,DATE '2026-04-14',TIMESTAMP '2026-02-03 09:12:00',TIMESTAMP '2026-04-14 16:20:00'),
  ('OPP-002','ACC-001','Northwind expansion',      'Closed Won',  12500.00,'USD',1.000000,DATE '2026-05-02',TIMESTAMP '2026-03-11 10:04:00',TIMESTAMP '2026-05-02 11:41:00'),
  ('OPP-003','ACC-002','Initech platform',         'Closed Won', 210000.00,'USD',1.000000,DATE '2026-05-27',TIMESTAMP '2026-01-19 14:33:00',TIMESTAMP '2026-05-27 17:02:00'),
  ('OPP-004','ACC-003','Umbra freight pilot',      'Closed Won',  67500.00,'EUR',1.082000,DATE '2026-06-09',TIMESTAMP '2026-04-01 08:55:00',TIMESTAMP '2026-06-09 12:10:00'),
  ('OPP-005','ACC-004','Kessler onboarding',       'Closed Won',  95250.00,'USD',1.000000,DATE '2026-06-30',TIMESTAMP '2026-05-06 13:20:00',TIMESTAMP '2026-06-30 18:45:00'),
  ('OPP-006','ACC-005','Ravenna line upgrade',     'Closed Won', 143000.00,'EUR',1.079500,DATE '2026-07-15',TIMESTAMP '2026-05-22 09:00:00',TIMESTAMP '2026-07-15 15:30:00'),
  ('OPP-007','ACC-006','Initech Labs tooling',     'Closed Won',  38400.00,'USD',1.000000,DATE '2026-07-21',TIMESTAMP '2026-06-02 11:15:00',TIMESTAMP '2026-07-21 10:05:00'),
  ('OPP-008','ACC-007','Halberd compliance',       'Closed Won', 176800.00,'GBP',1.271000,DATE '2026-07-28',TIMESTAMP '2026-04-18 16:40:00',TIMESTAMP '2026-07-28 09:25:00'),
  ('OPP-009','ACC-008','Solstice campaign suite',  'Closed Won',  54900.00,'USD',1.000000,DATE '2026-08-04',TIMESTAMP '2026-06-14 10:30:00',TIMESTAMP '2026-08-04 14:12:00'),
  ('OPP-010','ACC-002','Initech add-on seats',     'Closed Won',  29750.00,'USD',1.000000,DATE '2026-08-11',TIMESTAMP '2026-07-01 09:45:00',TIMESTAMP '2026-08-11 11:00:00'),
  ('OPP-011','ACC-003','Umbra route analytics',    'Closed Lost', 88000.00,'EUR',1.081000,DATE '2026-06-18',TIMESTAMP '2026-03-27 12:00:00',TIMESTAMP '2026-06-18 13:15:00'),
  ('OPP-012','ACC-004','Kessler regional rollout', 'Negotiation',320000.00,'USD',1.000000,DATE '2026-09-30',TIMESTAMP '2026-06-09 15:10:00',TIMESTAMP '2026-08-12 10:20:00'),
  ('OPP-013','ACC-005','Ravenna packaging',        'Closed Lost', 45000.00,'EUR',1.080000,DATE '2026-05-19',TIMESTAMP '2026-02-28 11:30:00',TIMESTAMP '2026-05-19 16:00:00'),
  ('OPP-014','ACC-001','Northwind pilot 2025',     'Closed Won',  31200.00,'USD',1.000000,DATE '2025-11-12',TIMESTAMP '2025-09-04 09:00:00',TIMESTAMP '2025-11-12 15:45:00'),
  ('OPP-015','ACC-007','Halberd data migration',   'Closed Won', 122400.00,'GBP',1.268000,DATE '2025-12-20',TIMESTAMP '2025-10-15 10:20:00',TIMESTAMP '2025-12-20 12:30:00'),
  ('OPP-016','ACC-008','Solstice retainer 2026',   'Closed Won',  84000.00,'USD',1.000000,DATE '2026-01-30',TIMESTAMP '2025-11-28 14:00:00',TIMESTAMP '2026-01-30 09:50:00'),
  ('OPP-017','ACC-002','Initech security review',  'Closed Won',  19800.00,'USD',1.000000,DATE '2026-02-27',TIMESTAMP '2026-01-08 08:40:00',TIMESTAMP '2026-02-27 17:15:00'),
  ('OPP-018','ACC-006','Initech Labs sandbox',     'Closed Won',  15600.00,'USD',1.000000,DATE '2026-03-13',TIMESTAMP '2026-01-30 13:50:00',TIMESTAMP '2026-03-13 10:35:00'),
  ('OPP-019','ACC-005','Ravenna maintenance',      'Closed Won',  27300.00,'EUR',1.077000,DATE '2026-03-31',TIMESTAMP '2026-02-11 09:25:00',TIMESTAMP '2026-03-31 16:40:00'),
  -- Amended after the month closed: close_date stays in April, amount revised in August.
  ('OPP-020','ACC-004','Kessler analytics tier',   'Closed Won', 118500.00,'USD',1.000000,DATE '2026-04-28',TIMESTAMP '2026-02-19 10:10:00',TIMESTAMP '2026-08-06 09:15:00'),
  -- Closed won with no close date at all.
  ('OPP-021','ACC-003','Umbra spot shipments',     'Closed Won',  22400.00,'EUR',1.080500,NULL,            TIMESTAMP '2026-05-14 11:05:00',TIMESTAMP '2026-06-01 10:00:00'),
  ('OPP-022','ACC-008','Solstice one-off creative','Closed Won',   9600.00,'USD',1.000000,NULL,            TIMESTAMP '2026-07-03 15:30:00',TIMESTAMP '2026-07-19 12:45:00'),
  -- Foreign currency with no conversion rate.
  ('OPP-023','ACC-005','Ravenna export order',     'Closed Won',  61250.00,'EUR',NULL,     DATE '2026-08-07',TIMESTAMP '2026-06-25 09:35:00',TIMESTAMP '2026-08-07 14:05:00'),
  -- Internal training account.
  ('OPP-024','ACC-009','Training scenario deal',   'Closed Won', 999999.00,'USD',1.000000,DATE '2026-08-01',TIMESTAMP '2026-07-30 09:00:00',TIMESTAMP '2026-08-01 09:30:00');

-- Line items. LI-901 and LI-902 reference opportunities absent from the
-- opportunity table (the orphan condition); the rest are well-formed.
INSERT INTO opportunity_line_item VALUES
  ('LI-001','OPP-001','Core subscription',   4, 9000.00),
  ('LI-002','OPP-001','Support tier 2',      1,12000.00),
  ('LI-003','OPP-003','Platform licence',   10,18000.00),
  ('LI-004','OPP-003','Implementation',      1,30000.00),
  ('LI-005','OPP-005','Onboarding services', 1,45250.00),
  ('LI-006','OPP-005','Training days',       5,10000.00),
  ('LI-007','OPP-006','Line hardware',       2,55000.00),
  ('LI-008','OPP-006','Commissioning',       1,33000.00),
  ('LI-009','OPP-008','Compliance module',   1,96800.00),
  ('LI-010','OPP-008','Audit support',       2,40000.00),
  ('LI-011','OPP-009','Campaign suite',      3,15300.00),
  ('LI-012','OPP-010','Additional seats',   25, 1190.00),
  ('LI-013','OPP-020','Analytics tier',      1,88500.00),
  ('LI-014','OPP-020','Data connectors',     2,15000.00),
  ('LI-015','OPP-023','Export packaging',    1,61250.00),
  ('LI-901','OPP-777','Orphaned add-on',     1, 4500.00),
  ('LI-902','OPP-778','Orphaned service',    2, 2250.00);
