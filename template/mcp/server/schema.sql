-- Demo schema for the reference MCP server. Synthetic, public-standards, no brand names.
-- Mirrors the dbt marts (fct_findings, dim_assets, dim_owners, dim_tickets) + a `tenant`
-- column on every table, so server-side tenant isolation is demonstrable end-to-end.

CREATE TABLE IF NOT EXISTS dim_owners (
  tenant   text NOT NULL,
  owner_id text NOT NULL,
  team     text,
  email    text,
  PRIMARY KEY (tenant, owner_id)
);

CREATE TABLE IF NOT EXISTS dim_assets (
  tenant             text NOT NULL,
  asset_id           text NOT NULL,
  hostname           text,
  is_internet_facing boolean DEFAULT false,
  environment        text,
  owner_id           text,
  business_unit      text,
  PRIMARY KEY (tenant, asset_id)
);

CREATE TABLE IF NOT EXISTS dim_tickets (
  tenant     text NOT NULL,
  ticket_id  text NOT NULL,
  state      text,
  assignee   text,
  sla_due_at timestamptz,
  PRIMARY KEY (tenant, ticket_id)
);

CREATE TABLE IF NOT EXISTS fct_findings (
  tenant                text NOT NULL,
  finding_id            text NOT NULL,
  asset_id              text,
  ticket_id             text,                 -- NULL => unassigned
  severity              text,                 -- normalized: critical|high|medium|low
  status                text,                 -- normalized: open|mitigated|closed
  detected_at           timestamptz,
  remediated_at         timestamptz,
  is_internet_facing    boolean DEFAULT false,
  is_exploitable        boolean DEFAULT false, -- KEV/EPSS-derived
  remediated_within_sla boolean DEFAULT false,
  ingested_at           timestamptz DEFAULT now(),
  PRIMARY KEY (tenant, finding_id)
);

-- Least-privilege read-only role the MCP server should connect as in production.
-- (Read-only is ALSO enforced at the session level by the engine: SET default_transaction_read_only.)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analytics_ro') THEN
    CREATE ROLE analytics_ro LOGIN PASSWORD 'readonly';
  END IF;
END $$;

GRANT CONNECT ON DATABASE analytics TO analytics_ro;
GRANT USAGE ON SCHEMA public TO analytics_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_ro;
