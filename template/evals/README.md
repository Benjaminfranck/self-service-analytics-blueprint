# ④ Evals & validation

Offline evals are to an analytics agent what unit tests are to software — they don't prove online
performance, but they catch critical gaps and let you measure change.

## Principles
- **Anchor ground truth** so evals don't go stale: prefer **grading the agent's query / metric
  resolution** over its live number; where you must assert a value, pin to a **snapshot date** or a
  stable fact table. A number-based eval rots the moment the underlying data moves.
- **Telemetry, not test logs.** Every run writes a row (`skill_version, git_sha, model, pass/fail,
  tokens, latency`) to a warehouse table → "did that change help?" is a query; slow regressions
  surface that a single CI run misses.
- **Per-domain gate (~90%).** A domain owner can't announce the agent to stakeholders until that
  domain's slice clears the gate — it forces reference-doc fixes *before* users see failures.
- **Ablation testing.** Hold the eval set fixed, change exactly one component, compare pass rates
  (~1hr/run). Put the before/after delta in the PR. Keep a **negative-results list** — additions
  that *hurt* (e.g. docs getting longer not better, a cheaper reviewer model losing accuracy).
- **Two eval flavors:** dashboard-based (common stakeholder questions, Claude-generated then
  human-validated) + long-tail (Claude generates plausible questions from business context/docs).
- **Harvest from corrections:** when a stakeholder corrects the agent in a thread, add an eval.
- **Targets:** offline accuracy ~100%, and *every correct answer should also hit the semantic layer*.

## Run
```bash
python evals/run_evals.py evals/gold_questions.yml   # exits non-zero below the gate (CI-friendly)
```

## Still unsolved (be honest about it)
**Silent wrong answers** — plausible, accepted without objection. Partial mitigations: the provenance
footer, mandatory human sign-off on leadership-bound outputs, and a daily standing eval of each
domain's top KPIs against the blessed dashboard. No fully robust solution yet.
