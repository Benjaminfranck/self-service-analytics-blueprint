"""Unit tests for the governed metric compiler — pure, no database required.

These verify the governance guarantees that matter most: tenant predicate always present,
allowlist-only (no raw SQL from the request), and fails-closed on anything unknown.
Run: pytest template/mcp/server/tests -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import engine  # noqa: E402


def test_list_metrics_returns_governed_catalog():
    names = {m["name"] for m in engine.list_metrics()}
    assert names == {"open_critical_findings", "mttr_hours", "critical_remediation_sla_rate"}
    assert all(m["owner"] == "security-analytics" for m in engine.list_metrics())


def test_open_critical_sql_is_correct_and_unjoined():
    sql = engine.build_sql("open_critical_findings")
    assert "count(*) AS open_critical_findings" in sql
    assert "f.severity = 'critical'" in sql and "f.status = 'open'" in sql
    assert "JOIN" not in sql  # no dimensions/filters that need a join


def test_tenant_predicate_always_injected():
    # The ONLY bound parameter is the tenant, and it is always present and first in WHERE.
    for metric in engine.METRICS:
        sql = engine.build_sql(metric)
        assert "WHERE f.tenant = %(tenant)s" in sql
        assert sql.count("%(tenant)s") == 1


def test_internet_facing_by_team_emits_both_joins_and_groupby():
    sql = engine.build_sql(
        "open_critical_findings",
        dimensions=["owner.team"],
        filters=["asset.is_internet_facing = true", "time.last_30_days"],
        order_by="open_critical_findings desc",
    )
    assert "JOIN dim_assets a" in sql and "JOIN dim_owners o" in sql
    assert "a.is_internet_facing = true" in sql
    assert "f.detected_at >= now() - interval '30 days'" in sql
    assert "GROUP BY o.team" in sql
    assert sql.strip().endswith("ORDER BY open_critical_findings desc;")


def test_ratio_metric_uses_filtered_aggregates_and_nullif():
    sql = engine.build_sql("critical_remediation_sla_rate", dimensions=["asset.business_unit"])
    assert "filter (where f.status = 'closed' and f.remediated_within_sla)" in sql
    assert "nullif(" in sql
    assert "JOIN dim_assets a" in sql and "GROUP BY a.business_unit" in sql


def test_unknown_metric_fails_closed():
    with pytest.raises(engine.MetricError) as ei:
        engine.build_sql("agent_blast_radius_score")
    assert ei.value.code == "no_such_metric"
    assert "open_critical_findings" in ei.value.suggestions


def test_unknown_dimension_fails_closed():
    with pytest.raises(engine.MetricError) as ei:
        engine.build_sql("open_critical_findings", dimensions=["owner.salary"])
    assert ei.value.code == "unknown_dimension"


def test_unknown_grain_and_order_by_fail_closed():
    with pytest.raises(engine.MetricError) as ei:
        engine.build_sql("open_critical_findings", grain="century")
    assert ei.value.code == "unknown_grain"
    with pytest.raises(engine.MetricError) as ei2:
        engine.build_sql("open_critical_findings", order_by="; drop table fct_findings")
    assert ei2.value.code == "unknown_order_by"


def test_filters_are_allowlisted_no_raw_sql():
    # An arbitrary predicate (injection attempt) is rejected — only named filters are allowed.
    with pytest.raises(engine.MetricError) as ei:
        engine.build_sql("open_critical_findings", filters=["1=1 OR f.tenant <> 'x'"])
    assert ei.value.code == "unknown_filter"
