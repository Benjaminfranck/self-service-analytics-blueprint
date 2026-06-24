-- Synthetic seed data. Two tenants ('acme', 'globex' — generic placeholders) so tenant isolation
-- is observable: an 'acme' query must never see 'globex' rows. Timestamps are relative to now()
-- so the last-30-days / this-quarter filters always have data. No real org, asset, or person.

-- ============================ tenant: acme ============================
INSERT INTO dim_owners (tenant, owner_id, team, email) VALUES
  ('acme','o1','payments','payments@example.com'),
  ('acme','o2','platform','platform@example.com'),
  ('acme','o3','data','data@example.com');

INSERT INTO dim_assets (tenant, asset_id, hostname, is_internet_facing, environment, owner_id, business_unit) VALUES
  ('acme','a1','web-01', true,  'prod','o1','retail'),
  ('acme','a2','api-01', true,  'prod','o2','platform'),
  ('acme','a3','db-01',  false, 'prod','o3','data'),
  ('acme','a4','lb-01',  true,  'prod','o1','retail');

INSERT INTO dim_tickets (tenant, ticket_id, state, assignee, sla_due_at) VALUES
  ('acme','t1','open','o1', now() + interval '2 days'),
  ('acme','t5','closed','o1', now() - interval '28 days'),
  ('acme','t6','closed','o2', now() - interval '22 days');

-- finding_id, asset, ticket, severity, status, detected (days ago), remediated, IF(cosmetic), exploitable, within_sla
INSERT INTO fct_findings
  (tenant, finding_id, asset_id, ticket_id, severity, status, detected_at, remediated_at, is_internet_facing, is_exploitable, remediated_within_sla, ingested_at) VALUES
  ('acme','f1','a1','t1','critical','open',      now()-interval '2 days',  NULL,                      true,  true,  false, now()-interval '1 hour'),
  ('acme','f2','a1', NULL,'critical','open',      now()-interval '5 days',  NULL,                      true,  true,  false, now()-interval '1 hour'),
  ('acme','f3','a2','t2','critical','open',       now()-interval '10 days', NULL,                      true,  true,  false, now()-interval '1 hour'),
  ('acme','f4','a2','t3','critical','open',       now()-interval '20 days', NULL,                      true,  false, false, now()-interval '1 hour'),
  ('acme','f5','a4', NULL,'critical','open',      now()-interval '1 days',  NULL,                      true,  true,  false, now()-interval '1 hour'),
  ('acme','f6','a3','t4','critical','open',       now()-interval '3 days',  NULL,                      false, true,  false, now()-interval '1 hour'),
  ('acme','f7','a1','t5','critical','closed',     now()-interval '30 days', now()-interval '28 days',  true,  true,  true,  now()-interval '1 hour'),
  ('acme','f8','a2','t6','critical','closed',     now()-interval '25 days', now()-interval '22 days',  true,  true,  true,  now()-interval '1 hour'),
  ('acme','f9','a3','t7','critical','closed',     now()-interval '40 days', now()-interval '35 days',  false, true,  false, now()-interval '1 hour'),
  ('acme','f10','a1','t8','high','open',          now()-interval '4 days',  NULL,                      true,  false, false, now()-interval '1 hour'),
  ('acme','f11','a2','t9','high','mitigated',     now()-interval '6 days',  NULL,                      true,  false, false, now()-interval '1 hour'),
  ('acme','f12','a3','t10','medium','open',       now()-interval '8 days',  NULL,                      false, false, false, now()-interval '1 hour'),
  ('acme','f13','a4','t11','low','open',          now()-interval '9 days',  NULL,                      true,  false, false, now()-interval '1 hour'),
  ('acme','f14','a1','t12','high','closed',       now()-interval '15 days', now()-interval '14 days',  true,  false, true,  now()-interval '1 hour');

-- ============================ tenant: globex (isolation check) ============================
INSERT INTO dim_owners (tenant, owner_id, team, email) VALUES
  ('globex','o1','infra','infra@example.com');

INSERT INTO dim_assets (tenant, asset_id, hostname, is_internet_facing, environment, owner_id, business_unit) VALUES
  ('globex','a1','gx-web', true,  'prod','o1','corp'),
  ('globex','a2','gx-db',  false, 'prod','o1','corp');

INSERT INTO fct_findings
  (tenant, finding_id, asset_id, ticket_id, severity, status, detected_at, remediated_at, is_internet_facing, is_exploitable, remediated_within_sla, ingested_at) VALUES
  ('globex','g1','a1','t1','critical','open',   now()-interval '2 days',  NULL,                     true,  true,  false, now()-interval '2 hours'),
  ('globex','g2','a1', NULL,'critical','open',  now()-interval '3 days',  NULL,                     true,  true,  false, now()-interval '2 hours'),
  ('globex','g3','a2','t2','high','open',       now()-interval '4 days',  NULL,                     false, false, false, now()-interval '2 hours'),
  ('globex','g4','a1','t3','critical','closed', now()-interval '20 days', now()-interval '18 days', true,  true,  true,  now()-interval '2 hours'),
  ('globex','g5','a2', NULL,'medium','open',    now()-interval '5 days',  NULL,                     false, false, false, now()-interval '2 hours'),
  ('globex','g6','a1','t4','critical','open',   now()-interval '6 days',  NULL,                     true,  true,  false, now()-interval '2 hours');
