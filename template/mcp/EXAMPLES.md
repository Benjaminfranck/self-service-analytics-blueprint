# MCP — worked request/response examples

Concrete payloads for the question: *"How many open critical findings are on internet-facing
assets, by team, last 30 days?"* MCP tools are JSON-RPC `tools/call`; below shows the **arguments
the agent sends** and the **result the server returns**. Note the agent never sends SQL — it sends a
structured metric request; the **server** compiles and runs the SQL read-only.

---

## 1) `list_metrics` — discover the governed catalog (metadata, no query)
**Agent sends:** `{ "name": "list_metrics", "arguments": {} }`
**Server returns:**
```json
{
  "metrics": [
    { "name": "open_critical_findings", "label": "Open Critical Findings",
      "dimensions": ["owner.team", "asset.business_unit", "asset.is_internet_facing", "detected_at"],
      "owner": "security-analytics", "tier": "gold", "additivity": "additive" },
    { "name": "mttr_hours", "label": "MTTR (hours)", "owner": "security-analytics",
      "tier": "gold", "additivity": "non-additive (average)" },
    { "name": "critical_remediation_sla_rate", "label": "Critical SLA Compliance %",
      "owner": "security-analytics", "tier": "gold", "additivity": "non-additive (ratio)" }
  ]
}
```

## 2) `resolve_entity` — map the question's nouns to entities + join paths (metadata)
**Agent sends:** `{ "name": "resolve_entity", "arguments": { "terms": ["team", "internet-facing assets"] } }`
**Server returns:**
```json
{
  "resolved": {
    "team": { "entity": "owner", "attribute": "owner.team",
              "join": "dim_assets.owner_id = dim_owners.owner_id" },
    "internet-facing assets": { "entity": "asset", "filter": "asset.is_internet_facing = true",
              "join": "fct_findings.asset_id = dim_assets.asset_id" }
  }
}
```

## 3) `compile_metric` — the data call (agent picks the metric; SERVER writes + runs the SQL)
**Agent sends (NOT SQL — a structured request):**
```json
{
  "name": "compile_metric",
  "arguments": {
    "metric": "open_critical_findings",
    "dimensions": ["owner.team"],
    "filters": ["asset.is_internet_facing = true", "time.last_30_days"],
    "order_by": "open_critical_findings desc"
  }
}
```
**Server returns — rows + the generated SQL (as provenance) + freshness:**
```json
{
  "metric": "open_critical_findings",
  "rows": [
    { "team": "payments", "open_critical_findings": 18 },
    { "team": "platform", "open_critical_findings": 7 },
    { "team": "data",     "open_critical_findings": 3 }
  ],
  "compiled_sql": "SELECT o.team, count(*) AS open_critical_findings\nFROM fct_findings f\nJOIN dim_assets a  ON a.asset_id = f.asset_id\nJOIN dim_owners o  ON o.owner_id = a.owner_id\nWHERE f.tenant = :tenant            -- injected by the server, never by the agent\n  AND f.severity = 'critical' AND f.status = 'open'\n  AND a.is_internet_facing\n  AND f.detected_at >= dateadd('day', -30, current_date)\nGROUP BY o.team\nORDER BY open_critical_findings DESC",
  "provenance": {
    "source_tier": "semantic layer",
    "metric_owner": "security-analytics",
    "freshness": "2026-06-23T13:40:00Z",
    "tenant_scoped": true,
    "rows_scanned": 482931,
    "latency_ms": 214
  }
}
```
The agent then renders the answer + the **provenance footer** built from `provenance`:
> Open critical findings on internet-facing assets, last 30 days, by team: **payments 18 · platform 7 · data 3**.
> *Source: semantic layer · Freshness: 2026-06-23 13:40 UTC · Owner: security-analytics · Reviewed: sql-reviewer ✓ round 1*

## 4) Fails CLOSED — an out-of-scope ask returns an error + a route, never a guess
**Agent sends:** `{ "name": "compile_metric", "arguments": { "metric": "agent_blast_radius_score" } }`
**Server returns:**
```json
{
  "error": "no_such_metric",
  "message": "No governed metric 'agent_blast_radius_score'. Did not guess.",
  "suggestions": ["open_critical_findings", "critical_remediation_sla_rate"],
  "fallback": "Use get_reference_doc('findings') for a constrained, reviewer-gated raw-SQL path; or open a PR to add the metric."
}
```
*This is the trust property: an unknown/ambiguous request fails with an error and a route — it does **not** fabricate a plausible-but-wrong number.*

## 5) `source_freshness` — for the footer (metadata)
**Agent sends:** `{ "name": "source_freshness", "arguments": { "source": "fabric.findings_normalized" } }`
**Server returns:** `{ "max_date": "2026-06-23T13:40:00Z", "status": "fresh", "warn_after_h": 2, "error_after_h": 6 }`

---

**Takeaway:** the MCP serves **(a) metadata** (catalog, entities/joins, freshness, lineage), **(b) data**
via `compile_metric` (the server generates + runs the SQL from a *structured* request), and **(c) the
generated SQL back as a provenance artifact** — never a raw-SQL-in execution path. Governance lives at
that boundary: the agent can only ask for governed metrics over governed dimensions.
