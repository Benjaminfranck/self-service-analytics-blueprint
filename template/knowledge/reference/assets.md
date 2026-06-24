<!-- ⑧ REFERENCE DOC (LLM-facing) — assets / coverage.
     Routed here from findings.md for inventory/coverage questions (not finding counts). -->

# Assets & Coverage

## Quick Reference
**Business Context** — `dim_assets` is the **asset golden record** (one row per resolved asset). Use it
for inventory, internet-facing exposure, ownership, and **control coverage** — not for counting findings.
**Entity Grain** — one row per resolved `asset_id`.
**Standard Hygiene Filter** — decommissioned assets excluded (`is_decommissioned = false`, baked into `dim_assets`).

## Dimensions
- **is_internet_facing** (bool) · **environment** · **business_unit** · **owner / team** (via `dim_owners`) · **hostname**.

## Key Tables
### dim_assets — **certified, canonical (golden record)**
- **Grain:** one `asset_id`. **Use for:** inventory, exposure, ownership, coverage.
- **Do NOT count findings off this table** — join to `fct_findings` and aggregate findings first.

## Common Query Patterns
- **Coverage gap:** assets missing a required control = `dim_assets LEFT JOIN <control_source> WHERE control IS NULL`.
- **Exposure:** filter `is_internet_facing = true`.
- **Ownership rollup:** join `dim_owners` for team / business_unit.

## Gotchas (wrong-answer modes a senior analyst warns about)
- **Fan-out:** joining 1 asset → N findings then `SUM`-ing an asset attribute double-counts — aggregate findings first.
- **"Active assets" is ambiguous:** seen-in-last-30d vs non-decommissioned — confirm (default: non-decommissioned).

## Routing triggers
- IF findings / vulnerabilities → `reference/findings.md`.
- IF board-level risk → `reference/risk.md`.

## Cross-References
`reference/findings.md` · `reference/risk.md` · `business_context/glossary.md`
