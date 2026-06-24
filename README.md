# Self-Service Data Analytics — A Governance-First Blueprint

> A reusable framework **and** a copyable repo scaffold for **trustworthy, AI-driven natural-language
> analytics** on any data warehouse — built governance-first, so a plain-language question returns an
> answer you can *act on*, not a confident-but-wrong number.

**→ Read [`GUIDE.md`](./GUIDE.md) for the full framework.** This README is the two-minute orientation.

---

## The problem this solves

In software there are many right answers and tests catch the wrong ones. In analytics there's usually
**one** right answer and **no test proves it** — so an LLM that writes SQL over raw tables fails *open*:
it ships a plausible, confident, **wrong** number that nobody questions. On sensitive data (security,
finance, health) that isn't a bad chart — it's a missed signal.

**The bet:** stop trying to make the model smarter; make the **context** unambiguous. Map a question to
a **governed metric**, and the SQL writes itself — correctly, the same way, on every surface.

> *The model is rarely the bottleneck — the governed context layer is.*

## The architecture — four stacked layers

```
+----------------------------------------------------------------------+
|  (4) VALIDATION    offline evals · per-domain accuracy gate · ablation|
|                    adversarial-review sub-agent · provenance footer   |
|                    passive monitoring (semantic-layer-use %, corrections)|
+----------------------------------------------------------------------+
|  (3) SKILLS        knowledge skill (thin router) + workflow skill     |
|     (procedural)   + adversarial reviewer · served via MCP            |
+----------------------------------------------------------------------+
|  (2) SOURCES OF TRUTH (declarative · what the agent consults)         |
|   - Semantic layer  (compiled metric/dimension defs · consulted FIRST)|
|   - Lineage / transformation graph (which model feeds what; freshness)|
|   - Query corpus    (historical SQL · CURATED into refs, not read raw)|
|   - Business-context KB (glossary, initiatives, decision logs, org)   |
+----------------------------------------------------------------------+
|  (1) DATA FOUNDATIONS  canonical, owned, consumption-ready datasets   |
|                        (dimensional models) · metadata as a product   |
|                        · enforced by tooling + CI + mandate           |
+----------------------------------------------------------------------+
   sources -> warehouse -> dbt transforms -> (layers above) -> NL query · dashboards
```

**The order is the lesson — start at the bottom.** A handful of canonical datasets, a thin router skill,
and a few dozen evals capture most of the value before anything fancy.

## What's in here

| Path | What it is |
|---|---|
| [`GUIDE.md`](./GUIDE.md) | The framework: principle, architecture, runtime, components, phased rollout. |
| [`template/`](./template) | A real, copyable repo scaffold — one directory per concept. |
| `template/models/` | (1) canonical dbt datasets + contracts/owner/tests |
| `template/semantic/` | (2) semantic layer (metrics + additivity) + entity/relationship graph |
| `template/knowledge/` | (2/5) reference docs, business context, query corpus, lineage |
| `template/.claude/skills/` | (3) router · workflow · adversarial reviewer |
| `template/mcp/` | distribution — serve the governed layer over MCP |
| `template/evals/` | (4) gold questions + harness (per-domain gate + telemetry) |
| `template/governance/` | (4) metric governance · provenance footer · tenant isolation |
| `template/.github/workflows/` | (4) CI: paired-doc gate + dbt build + eval gate |

## Quickstart — adapt it in six steps

1. Pick ~5 **canonical** datasets for ONE domain → fill `template/models/marts/`.
2. Write **one** reference doc + the **router skill**.
3. Write **a few dozen** evals (`template/evals/gold_questions.yml`).
4. Define the domain's **metrics** (`template/semantic/`) — humans own the definitions.
5. Wire **colocation CI** + the **per-domain eval gate**.
6. Add the **workflow + adversarial** skills, then the business-context KB, then expose over **MCP**.

## Tech stack (reference — all swappable)

dbt + a MetricFlow-style semantic layer + Claude Code Skills + MCP + an eval harness + CI. Swap the
warehouse (Snowflake / BigQuery / ClickHouse), the semantic engine (Cube / LookML / Malloy), even the
transport — the **roles** are what matter, not the tools.

## A note on the worked example

The template ships with **one worked example — security / vulnerability-finding analytics** — because a
concrete domain makes the patterns legible. It uses **only public standards** (CVSS, EPSS, KEV, MTTR,
SLA) and **synthetic, illustrative data**. Repoint the `<placeholders>` at any domain; `GUIDE.md` §7
shows how.

## Disclaimer

This is an **illustrative reference blueprint**. All data, metrics, table names, and examples are
**synthetic** and for demonstration only. It is **not affiliated with, derived from, or representative
of any employer, product, or customer**, and describes no proprietary system. Provided "as is" under the
MIT License.

## License

MIT © 2026 Benjamin Franck. See [`LICENSE`](./LICENSE).
