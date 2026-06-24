<!-- ⑧ REFERENCE DOC — written FOR THE LLM, not humans. The router points here when the
     semantic layer lacks coverage. Consistent structure (article's appendix template).
     Encode routing triggers + gotchas, NOT brittle step-by-step recipes that go stale. -->

# Findings Tables

## Quick Reference
**Business Context** — A "finding" is a deduplicated vulnerability/exposure on an asset, normalized
across scanners (multiple vendors + app scanners). One real issue seen by N tools = ONE finding.
**Entity Grain** — `fct_findings`: one row per `finding_id`. `dim_assets`: one row per resolved `asset_id`.
**Standard Hygiene Filter** — `is_suppressed = false` (already baked into `fct_findings`; never drop or re-add).

## Dimensions (how the same concept is encoded)
- **severity** — normalized to `critical|high|medium|low`. NOT the raw CVSS/EPSS/vendor value (those are reconciled upstream by a governed normalization transform). If a user says "critical," confirm they mean normalized severity, not a tuned risk band.
- **status** — `open | mitigated | closed`. "Open" EXCLUDES mitigated and closed.
- **is_internet_facing** (asset attr) · **is_exploitable** (KEV/EPSS-derived flag) · **business_unit / team** (via `dim_owners`).
- **time** — `detected_at` (default grain: day; default window: last 30d; UTC).

## Key Tables
### fct_findings  — **certified, canonical**
- **Grain:** one finding_id. **Scope/exclusions:** suppressed findings excluded.
- **Use for:** counts, MTTR, SLA, trend, aging of findings. **Join keys:** `asset_id` → `dim_assets`; `ticket_id` → `dim_tickets` (null = unassigned).
- **Required filters:** none beyond hygiene (baked in).
### dim_assets  — **certified, canonical (golden record)**
- **Grain:** one asset_id. **Use for:** asset context, internet-facing, ownership, coverage. **Do NOT** count findings off this table.

## Gotchas (wrong-answer modes a senior analyst warns about)
- **Distinct asset counts don't sum** across slices — use `assets_affected` (non-additive) or an HLL sketch in rollups; never `sum()` daily distincts.
- **MTTR is an average** — recompute from base rows; don't average daily averages.
- **"Unassigned" ≠ status** — it's `ticket_id IS NULL`, independent of `status`.
- **Fan-out:** joining `dim_assets` 1→N `fct_findings` then `SUM`-ing an asset attribute double-counts — aggregate findings first.
- **Severity drift:** if a user re-weights severity, "critical" may diverge from the normalized enum — confirm which they mean.

## Best Practices / Common Query Patterns
- Prefer the **semantic-layer metric** (`open_critical_findings`, `mttr_hours`, `critical_remediation_sla_rate`) over hand SQL.
- Trend: metric by `detected_at` (day/week). SLA: use the ratio metric; decompose numerator vs denominator.
- Coverage gaps: `dim_assets LEFT JOIN <control source> WHERE control IS NULL`.

## Routing triggers
- IF the question is about **risk scoring / board-level risk** → that's a governed board-level risk score, NOT a raw finding count. Route to `reference/risk.md`.
- IF about **asset inventory / coverage** (not findings) → `reference/assets.md`.

## Cross-References
`reference/assets.md` · `reference/risk.md` · `business_context/glossary.md`
