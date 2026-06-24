<!-- ⑧ REFERENCE DOC (LLM-facing) — board-level risk scoring.
     Routed here from findings.md when a question is about risk, not raw finding counts. -->

# Risk Score

## Quick Reference
**Business Context** — A board-level "risk score" is a **governed, composite metric**, NOT a raw count
of findings. It blends severity, exploitability, asset exposure, and business context into one owned
number. Never derive it from a raw finding count.
**Entity Grain** — one risk score per scored entity (asset · business unit · org), per snapshot date.
**Standard Hygiene Filter** — scored only on in-scope, non-decommissioned assets.

## Dimensions
- **scope** — `asset | business_unit | org`.
- **as_of** — snapshot date. Risk is **semi-additive**: snapshot per period, do NOT sum across time.

## Key Tables
### the governed risk model (e.g. `fct_risk_scores`) — **certified, canonical**
- **Grain:** one row per `(entity, as_of)`. **Use for:** board/exec risk narrative + trend.
- **Do NOT** reconstruct it from `fct_findings` — the governed score is owned separately.

## Gotchas (wrong-answer modes a senior analyst warns about)
- **Risk ≠ finding count.** "How many criticals" → `reference/findings.md`; "what's our risk" → the governed score.
- **Semi-additive:** snapshot per period; never sum scores over time or across overlapping scopes.
- **Tunable but governed:** a scope may use a tuned weighting — confirm default vs tuned before answering.

## Routing triggers
- IF raw finding counts / MTTR / SLA → `reference/findings.md`.
- IF asset inventory / coverage → `reference/assets.md`.

## Cross-References
`reference/findings.md` · `reference/assets.md` · `business_context/glossary.md`
