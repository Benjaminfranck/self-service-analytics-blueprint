"""End-to-end demo: run governed metric requests through the engine against Postgres and print
rows + the compiled SQL + a provenance footer. No MCP client required — this is the "watch it
work" path. Exits non-zero on any unexpected failure (CI-friendly).

Usage:  WAREHOUSE_DSN=postgresql://postgres@localhost:55432/analytics DEMO_TENANT=acme python demo.py
"""
from __future__ import annotations
import os
import sys

import engine

QUESTIONS = [
    ("How many open critical findings are there right now?",
     dict(metric="open_critical_findings")),
    ("Open critical findings on internet-facing assets, by team, last 30 days",
     dict(metric="open_critical_findings", dimensions=["owner.team"],
          filters=["asset.is_internet_facing = true", "time.last_30_days"],
          order_by="open_critical_findings desc")),
    ("MTTR (hours) for criticals, this quarter",
     dict(metric="mttr_hours", filters=["finding.severity = 'critical'", "time.this_quarter"])),
    ("Critical SLA compliance rate, by business unit",
     dict(metric="critical_remediation_sla_rate", dimensions=["asset.business_unit"])),
]


def _footer(r: dict) -> str:
    return (f"Source: {r['source_tier']} · Reviewed: (demo — reviewer not run) · "
            f"Freshness: {r['freshness']} · Owner: {r['metric_owner']} · "
            f"tenant_scoped: {r['tenant_scoped']}")


def main() -> None:
    tenant = os.environ.get("DEMO_TENANT", "acme")
    print(f"\n=== Self-Service Analytics — end-to-end demo (tenant: {tenant}) ===")
    failures = 0

    for question, req in QUESTIONS:
        print(f"\nQ: {question}")
        try:
            r = engine.compile_metric(**req)
            if not r["rows"]:
                print("    (no rows)")
            for row in r["rows"]:
                print("   ", row)
            print("    SQL:")
            for line in r["compiled_sql"].splitlines():
                print("        " + line)
            print(f"    params: {r['params']}")
            print("    " + _footer(r))
        except engine.MetricError as e:
            print("    UNEXPECTED ERROR:", e.to_dict())
            failures += 1

    # fails-closed: an out-of-scope ask returns an error + a route, never a fabricated number
    print("\nQ: (adversarial) ask for a non-existent metric 'agent_blast_radius_score'")
    try:
        engine.compile_metric(metric="agent_blast_radius_score")
        print("    !!! should have failed closed but did not")
        failures += 1
    except engine.MetricError as e:
        print("    fails CLOSED →", e.to_dict())

    print(f"\n=== done · {failures} unexpected failure(s) ===")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
