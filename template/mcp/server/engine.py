"""Reference MCP engine — text-to-metric compiler + read-only Postgres execution.

SCOPE: a *reference* compiler for the example security metrics in ../../semantic/findings.yml.
For production, swap in dbt Semantic Layer / MetricFlow or Cube. The governance properties are the
point and they hold regardless of the compiler:
  - the agent selects a GOVERNED metric + dimensions; it never sends SQL;
  - THIS server compiles + runs read-only SQL;
  - the tenant predicate is injected HERE (never from the request);
  - unknown metrics/dimensions/filters FAIL CLOSED (error + suggestions), never a guess.
"""
from __future__ import annotations
import os
from datetime import date, datetime
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row

# --- governed registry (mirrors semantic/findings.yml + entities_graph.yml) ------------------
BASE = "fct_findings f"

JOINS = {
    "assets": "JOIN dim_assets a ON a.asset_id = f.asset_id AND a.tenant = f.tenant",
    "owners": "JOIN dim_owners o ON o.owner_id = a.owner_id AND o.tenant = a.tenant",
}

# dimension name -> (sql_expr, output_alias, required joins)
DIMENSIONS = {
    "owner.team":               ("o.team",                "team",               ["assets", "owners"]),
    "asset.business_unit":      ("a.business_unit",        "business_unit",      ["assets"]),
    "asset.is_internet_facing": ("a.is_internet_facing",   "is_internet_facing", ["assets"]),
    "finding.severity":         ("f.severity",             "severity",           []),
    "finding.status":           ("f.status",               "status",             []),
}

# time grain -> sql expr on detected_at
GRAINS = {
    "day":   "date_trunc('day', f.detected_at)",
    "week":  "date_trunc('week', f.detected_at)",
    "month": "date_trunc('month', f.detected_at)",
}

# metric name -> definition (measures + base filters, from findings.yml)
METRICS = {
    "open_critical_findings": {
        "kind": "simple",
        "select": "count(*)",
        "alias": "open_critical_findings",
        "base_filters": ["f.severity = 'critical'", "f.status = 'open'"],
        "owner": "security-analytics",
    },
    "mttr_hours": {
        "kind": "simple",
        "select": "round(avg(extract(epoch from (f.remediated_at - f.detected_at)) / 3600.0)::numeric, 1)",
        "alias": "mttr_hours",
        "base_filters": ["f.remediated_at is not null"],
        "owner": "security-analytics",
    },
    "critical_remediation_sla_rate": {
        "kind": "ratio",
        "numerator": "count(*) filter (where f.status = 'closed' and f.remediated_within_sla)",
        "denominator": "count(*) filter (where f.severity = 'critical')",
        "alias": "critical_remediation_sla_rate",
        "base_filters": [],
        "owner": "security-analytics",
    },
}

# allowlisted named filters -> (sql_fragment, required joins). Fixed vocabulary: no raw user values.
NAMED_FILTERS = {
    "asset.is_internet_facing = true":  ("a.is_internet_facing = true",  ["assets"]),
    "asset.is_internet_facing = false": ("a.is_internet_facing = false", ["assets"]),
    "time.last_30_days":                ("f.detected_at >= now() - interval '30 days'", []),
    "time.this_quarter":                ("f.detected_at >= date_trunc('quarter', now())", []),
    "finding.ticket_id is null":        ("f.ticket_id is null", []),
    "finding.severity = 'critical'":    ("f.severity = 'critical'", []),
    "finding.severity = 'high'":        ("f.severity = 'high'", []),
}


class MetricError(Exception):
    """Raised when the agent asks for something not in the governed registry — fails closed."""
    def __init__(self, code: str, message: str, suggestions: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestions = suggestions or []

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message, "suggestions": self.suggestions}


def list_metrics() -> list[dict]:
    return [
        {"name": name, "kind": d["kind"], "owner": d["owner"], "tier": "gold",
         "dimensions": list(DIMENSIONS.keys())}
        for name, d in METRICS.items()
    ]


def _resolve_filters(filters: list[str]) -> tuple[list[str], list[str]]:
    frags, joins = [], []
    for fl in filters:
        key = fl.strip().lower()
        if key not in NAMED_FILTERS:
            raise MetricError("unknown_filter", f"No governed filter '{fl}'.",
                              suggestions=list(NAMED_FILTERS.keys()))
        frag, js = NAMED_FILTERS[key]
        frags.append(frag)
        joins += js
    return frags, joins


def build_sql(metric: str, dimensions=None, filters=None, grain=None,
              order_by=None, limit=None) -> str:
    """Compile a governed metric request to parameterized SQL. Pure — no DB. The only bound
    parameter is %(tenant)s (injected at execution); everything else is allowlisted."""
    dimensions = dimensions or []
    filters = filters or []
    if metric not in METRICS:
        raise MetricError("no_such_metric", f"No governed metric '{metric}'. Did not guess.",
                          suggestions=list(METRICS.keys()))
    m = METRICS[metric]
    needed, select_dims, group_dims = [], [], []

    if grain:
        if grain not in GRAINS:
            raise MetricError("unknown_grain", f"No grain '{grain}'.", suggestions=list(GRAINS.keys()))
        select_dims.append(f"{GRAINS[grain]} AS period")
        group_dims.append(GRAINS[grain])

    for d in dimensions:
        if d not in DIMENSIONS:
            raise MetricError("unknown_dimension", f"No governed dimension '{d}'.",
                              suggestions=list(DIMENSIONS.keys()))
        expr, alias, js = DIMENSIONS[d]
        select_dims.append(f"{expr} AS {alias}")
        group_dims.append(expr)
        needed += js

    ffrags, fjoins = _resolve_filters(filters)
    needed += fjoins

    if m["kind"] == "ratio":
        measure = f"round(({m['numerator']})::numeric / nullif({m['denominator']}, 0), 3) AS {m['alias']}"
    else:
        measure = f"{m['select']} AS {m['alias']}"

    join_sql = "".join("\n  " + JOINS[j] for j in ("assets", "owners") if j in needed)
    where = ["f.tenant = %(tenant)s"] + m["base_filters"] + ffrags
    sel = ", ".join(select_dims + [measure]) if select_dims else measure
    sql = f"SELECT {sel}\nFROM {BASE}{join_sql}\nWHERE " + "\n  AND ".join(where)
    if group_dims:
        sql += "\nGROUP BY " + ", ".join(group_dims)
    if order_by:
        allowed = {alias for (_, alias, _) in DIMENSIONS.values()} | {m["alias"], "period"}
        ob = order_by.replace(" desc", "").replace(" asc", "").strip()
        if ob not in allowed:
            raise MetricError("unknown_order_by", f"Cannot order by '{order_by}'.",
                              suggestions=sorted(allowed))
        sql += f"\nORDER BY {order_by}"
    if limit:
        sql += f"\nLIMIT {int(limit)}"
    return sql + ";"


def _jsonable(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


def _connect():
    dsn = os.environ.get("WAREHOUSE_DSN")
    if not dsn:
        raise MetricError("no_dsn", "WAREHOUSE_DSN not set. Copy .env.example and export it.")
    conn = psycopg.connect(dsn, row_factory=dict_row, autocommit=True)
    timeout = int(os.environ.get("STATEMENT_TIMEOUT_MS", "5000"))
    conn.execute("SET default_transaction_read_only = on")   # writes fail even if the role could
    conn.execute(f"SET statement_timeout = {timeout}")
    return conn


def compile_metric(metric, dimensions=None, filters=None, grain=None,
                   order_by=None, limit=None, tenant=None) -> dict:
    tenant = tenant or os.environ.get("DEMO_TENANT", "acme")
    sql = build_sql(metric, dimensions, filters, grain, order_by, limit)
    with _connect() as conn:
        rows = conn.execute(sql, {"tenant": tenant}).fetchall()
        fresh = conn.execute(
            "SELECT max(ingested_at) AS f FROM fct_findings WHERE tenant = %(tenant)s",
            {"tenant": tenant}).fetchone()["f"]
    rows = [{k: _jsonable(v) for k, v in r.items()} for r in rows]
    return {
        "metric": metric,
        "rows": rows,
        "compiled_sql": sql,
        "params": {"tenant": tenant},
        "freshness": fresh.isoformat() if fresh else None,
        "tenant_scoped": True,
        "source_tier": "semantic layer",
        "metric_owner": METRICS[metric]["owner"],
    }


def source_freshness(tenant=None) -> dict:
    tenant = tenant or os.environ.get("DEMO_TENANT", "acme")
    with _connect() as conn:
        row = conn.execute(
            "SELECT max(ingested_at) AS f, count(*) AS n FROM fct_findings WHERE tenant = %(tenant)s",
            {"tenant": tenant}).fetchone()
    return {"source": "fct_findings", "max_date": row["f"].isoformat() if row["f"] else None,
            "rows": row["n"], "status": "fresh" if row["f"] else "empty"}


def resolve_entity(terms: list[str]) -> dict:
    """Map question nouns to governed entities + join paths (metadata only)."""
    lookup = {
        "team": {"entity": "owner", "attribute": "owner.team", "join": JOINS["owners"]},
        "internet-facing": {"entity": "asset", "filter": "asset.is_internet_facing = true",
                            "join": JOINS["assets"]},
        "internet-facing assets": {"entity": "asset", "filter": "asset.is_internet_facing = true",
                                   "join": JOINS["assets"]},
        "business unit": {"entity": "asset", "attribute": "asset.business_unit", "join": JOINS["assets"]},
        "finding": {"entity": "finding", "primary_key": "finding_id"},
        "asset": {"entity": "asset", "primary_key": "asset_id", "join": JOINS["assets"]},
    }
    return {"resolved": {t: lookup.get(t.strip().lower(), {"entity": None, "note": "unrecognized noun"})
                         for t in terms}}
