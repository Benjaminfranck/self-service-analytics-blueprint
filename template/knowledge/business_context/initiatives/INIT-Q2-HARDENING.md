---
id: init-q2-hardening
doc_type: initiative
name: Q2 Internet-Facing Hardening Push
aliases: ["Q2 hardening push", "the hardening push", "Q2 exposure program", "HARD-2026"]
date_range: { start: 2026-04-01, end: 2026-06-30 }
owner_team: sec-ops
status: in_progress
success_metrics: [open_critical_findings, critical_remediation_sla_rate]   # metric IDs, NOT values
scope_filter: "is_internet_facing = true AND severity = 'critical'"
related_dashboards: ["bi://dashboards/q2-hardening"]
---

The Q2 Hardening Push is the sec-ops program to drive **open critical findings on
internet-facing assets** to zero by 2026-06-30. When someone asks "how is the Q2 hardening
push doing?", they mean: trend of `open_critical_findings` filtered to `is_internet_facing`,
plus `critical_remediation_sla_rate`, over the initiative's date range — resolved live through
the semantic layer (never quote a number cached here).

<!-- This file is the ambient-reference anchor: it maps a colloquial program name → the exact
     entities, filters, and governed metrics, so the agent answers what the user MEANT. -->
