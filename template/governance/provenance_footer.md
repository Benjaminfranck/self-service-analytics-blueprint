# ④ Provenance footer

Appended to **every** answer. It doesn't make the answer more correct — it lets the consumer judge
how much to trust it. A "raw table, freshness unknown" footer is a signal to verify before forwarding.

## Format
```
Source:    [ semantic layer | governed table | raw exploration ]   ← the trust hierarchy
Confidence:[ high | medium | low ]
Reviewed:  [ sql-reviewer ✓, round N | not reviewed ]
Freshness: [ max date present in the underlying data, e.g. 2026-06-23 14:00 UTC ]
Owner:     [ owning team / metric owner ]
```

## Field rules
- **Source** — the tier the answer came from. `semantic layer` is highest trust (governed metric);
  `governed table` (certified mart, ad-hoc agg); `raw exploration` is lowest (verify before sharing).
- **Confidence** — from the agent's self-consistency / reviewer verdict; `low` ⇒ recommend verification.
- **Reviewed** — whether the `sql-reviewer` sub-agent passed it and on which round.
- **Freshness** — the **max date in the data** (derived from lineage + `dbt source freshness`),
  not "now". Stale data with a confident number is the dangerous case.
- **Owner** — who to ask / who owns the metric (from `meta.owner` + lineage).

## Worked example
```
Open critical findings on internet-facing assets (last 30d), by team: [chart]
— SQL: SELECT o.team, count(*) ... (shown in full)
Source: semantic layer · Confidence: high · Reviewed: sql-reviewer ✓ round 1
Freshness: 2026-06-23 13:40 UTC · Owner: security-analytics
```

> Pair with **explicit human sign-off** on anything leadership/board-bound — the footer is necessary, not sufficient.
