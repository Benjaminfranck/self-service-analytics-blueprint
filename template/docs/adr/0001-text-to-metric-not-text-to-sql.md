# ADR 0001 — Ground NL analytics on the semantic layer (text-to-metric), not raw text-to-SQL

- **Status:** Accepted
- **Date:** <yyyy-mm-dd>
- **Owners:** <data-platform>

## Context
Users want natural-language answers. The naive approach lets the LLM write SQL over raw tables.
On analytics there's usually one correct answer with no deterministic proof — and on **security
data a plausible-but-wrong answer is a missed breach.** Text-to-SQL **fails open** (confident wrong
numbers, run-to-run inconsistency, hallucinated joins/columns). Benchmarks: frontier models scored
~51–62% via text-to-SQL vs **100% via a semantic layer** on in-scope questions; raw query-corpus
retrieval moved accuracy **<1 point** (structure, not access, is the bottleneck).

## Decision
The agent resolves questions to **governed metrics + dimensions in the semantic layer FIRST**
(text-to-metric). Raw SQL is a **fallback only** when the semantic layer lacks coverage, constrained
to entities/joins defined in the entity graph, and always passed through the adversarial reviewer +
provenance footer. Metric definitions are **human-owned** (Claude drafts docs, not definitions).

## Consequences
- ✅ Answers are **correct by construction** when a metric matches; the system **fails closed** (error) instead of misleading.
- ✅ No hallucinated joins/columns; consistent numbers across every surface; auditable provenance.
- ⚠️ Coverage is the lever — questions beyond modeled scope score ~0% via the semantic layer, so we
  must continuously expand metrics AND keep a constrained text-to-SQL fallback for ad-hoc discovery.
- ⚠️ Requires investment in the semantic layer + governance up front (slower first demo than raw text-to-SQL).

## Rejected alternatives
- **Raw text-to-SQL over the lake** — max flexibility, unacceptable trust on security data.
- **Curated canned Q&A only** — safe but doesn't scale to the long tail.
- **Raw query-corpus retrieval** — empirically moved accuracy <1 point.
