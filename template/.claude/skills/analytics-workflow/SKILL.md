---
name: analytics-workflow
version: 0.1.0
description: >
  The process a senior security-data analyst follows to answer a question end-to-end.
  Use alongside analytics-router for any non-trivial analysis. Encodes clarify → find →
  query → adversarial-review → report, plus reusable analysis patterns.
---

# Analytics Workflow ("unbook" / process skill)

Procedural knowledge — *how a senior analyst works*, not what a metric means (that's the
sources of truth). Follow the steps; reuse the patterns; never skip the review.

## The process
1. **Clarify the question.** Restate it. Resolve ambiguous entities/timeframes (ask if a wrong
   guess would mislead — on security data a wrong answer is a missed breach). Identify the persona
   (analyst → drill-down; manager → KPI; CISO/board → one number + trend).
2. **Find the source.** Semantic layer first (via `analytics-router`). If no coverage, the router's
   reference doc; pick the certified/canonical table (lineage-ranked), not a staging table.
3. **Build & run the query.** Use defined metrics; if raw SQL is unavoidable, take joins from the
   entity graph, apply the hygiene filter, run read-only with EXPLAIN first.
4. **Adversarial review (mandatory).** Pass the query + result to the `sql-reviewer` sub-agent.
   Fix every blocking finding and re-review. Do not self-certify.
5. **Report.** Lead with the answer; show the query; attach the **provenance footer**.
   Flag low confidence ("raw table, freshness unknown → verify before forwarding").

## Reusable analysis patterns (don't reinvent per request)
- **Trend over time** — metric by `detected_at` day/week; annotate the standard window.
- **Rate decomposition** — e.g. SLA rate = closed-in-SLA / criticals; break the ratio's drivers (numerator vs denominator movement) rather than reporting the ratio alone.
- **Funnel** — detected → triaged → ticketed → remediated → verified; conversion + drop-off per stage.
- **Cohort / aging** — findings by age bucket (open >30/60/90d); MTTR by severity.
- **Coverage** — assets missing a control (EDR/agent) = `dim_assets` LEFT JOIN coverage source where null.
- **Top-N + concentration** — top teams/BUs by open criticals; share of total (is risk concentrated?).
For each: pick the metric, the dimension to slice, the standard filter, and a guardrail check.

## Output contract
Answer → query shown → provenance footer → (if leadership-bound) explicit "needs human sign-off".
