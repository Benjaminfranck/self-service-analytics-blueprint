# ④ Query corpus — the most counter-intuitive lesson in the whole system

Historical SQL from dashboards, notebooks, and prior analyses *looks* like a goldmine: a record
of every question already answered correctly. **It isn't — not as a retrieval source.**

> Anthropic's ablation: giving the agent grep access to thousands of prior queries moved accuracy
> **< 1 point**. The answer was present for **~80%** of *failed* questions, and "answer present"
> did **not** predict "now gets it right." The bottleneck was **structure, not access** —
> unstructured retrieval can't map a new question to the right precedent.

## So what do you do with the corpus?
**Curate it into structure, don't read it raw:**
1. Mine it to discover the **canonical metrics** people actually compute → define them in `semantic/`.
2. Mine recurring shapes → the **reusable analysis patterns** in `analytics-workflow/SKILL.md`.
3. Distill domain gotchas → `knowledge/reference/*`.
4. Keep a small, **curated** few-shot set (`corpus.jsonl`) retrieved by **masked-skeleton similarity**
   (DAIL-SQL style), with **`metric_request` targets** (text-to-metric) — far more auditable than raw SQL.

Treat query history as **raw material for curation**, not a source of truth the agent reads directly.

## corpus.jsonl format
One JSON object per line: the NL question, a masked skeleton (domain words → `[MASK]`) for
similarity retrieval, the governed `metric_request` target, an illustrative `sql`, and validation
metadata. Retrieve top-k by masked-question embedding distance **and** query-skeleton similarity.
