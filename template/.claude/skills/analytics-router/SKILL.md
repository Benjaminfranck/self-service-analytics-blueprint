---
name: analytics-router
version: 0.1.0
description: >
  Use for ANY question about security analytics data (findings, vulnerabilities, assets,
  remediation, SLAs, coverage). Routes to the semantic layer first, then to per-domain
  reference docs. Loads the must-know business context every query needs.
---

# Security Analytics — Skill Instructions (thin router)

> This skill is a **router**, not a knowledge dump. It carries must-know context + the
> workflow, then points to ~N per-domain reference files. Keep it < 500 lines; push detail
> to `knowledge/reference/*`. Only this `description` is loaded up front — the body loads on demand.

## Executing queries
- Connect read-only. EXPLAIN/dry-run before executing. Never mutate.
- Connection priority: semantic-layer API → governed marts → (last resort) raw exploration.

## Semantic layer — REQUIRED FIRST STEP
1. **Load** the metric catalog (`semantic/findings.yml`, served via MCP `list_metrics`).
2. **Discover** whether the question maps to a defined metric (e.g. `open_critical_findings`, `mttr_hours`, `critical_remediation_sla_rate`) + dimensions (severity, status, team/business_unit, time).
3. **Compile + run** the metric. One metric → one number → the same number every surface returns.
4. **Fallback** to reference docs ONLY if there is no metric coverage. Log the gap.
- Default date window = last 30 days unless asked; timezone = UTC.

## PART 1 — MUST KNOW (read first for every request)
**Quick-start workflow:** (1) restate the question; (2) resolve ambiguous entities (below);
(3) try the semantic layer; (4) if no coverage, open the domain reference doc; (5) build the
query from the entity graph's join paths; (6) run read-only; (7) loop through `sql-reviewer`;
(8) answer WITH the provenance footer.
**Business context / disambiguation (clarify, don't guess):**
- "critical" → `severity = 'critical'` (normalized), NOT a customer-tuned risk band — confirm if ambiguous.
- "exploitable" → `is_exploitable` (KEV/EPSS-derived), not raw CVSS.
- "open" excludes `mitigated` and `closed`. "Unassigned" = `ticket_id IS NULL`.
- Ambient terms ("the Q2 hardening push") → resolve via `knowledge/business_context/`.
**Data integrity:** every findings query inherits the standard hygiene filter (`is_suppressed = false`) — it's baked into `fct_findings`; do not re-add or drop it.

## PART 2 — HOW TO DO (during execution)
- **Technical execution:** prefer the metric API; if writing SQL, reference only entities/columns in `semantic/entities_graph.yml`; take join paths from edge `join:` clauses (never invent a join); cap traversal at 2 hops.
- **Analysis best practices:** apply the hygiene filter; pick the certified/canonical table (lineage-ranked); mind additivity (distinct counts/ratios don't roll up); **always run `sql-reviewer` before the final answer; fix blocking findings and re-review — do not self-certify.**
- **Report with the provenance footer** (see `governance/provenance_footer.md`).

## PART 3 — DATA REFERENCES & RESOURCES
**Knowledge base navigation (route here when the semantic layer lacks coverage):**
- Findings / vulnerabilities → `knowledge/reference/findings.md`
- Assets / coverage → `knowledge/reference/assets.md`
- Business terms & initiatives → `knowledge/business_context/`
- `<add one entry per domain — keep each domain's detail in its own reference file>`

**Troubleshooting:** no metric coverage → reference doc + open a PR to add the metric. Stale/odd number → check freshness (footer) + lineage; if a user corrects you, the correction-harvesting agent will PR a doc fix.
