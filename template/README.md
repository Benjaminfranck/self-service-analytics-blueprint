# Self-Service Analytics — reusable template

A copyable skeleton for a **Claude-powered self-service analytics** system, structured exactly around the four layers in `../GUIDE.md` (Data foundations → Sources of truth → Skills → Validation). The worked example is **security** (vulnerability findings + assets); repoint the `<placeholders>` at any domain.

## What's here
| Path | Layer | Role |
|---|---|---|
| `models/` | (1) foundations | dbt staging + canonical marts (`fct_findings`, `dim_assets`) with tests/contracts/ownership |
| `semantic/findings.yml` | (2) semantic layer | governed metric + dimension definitions (consulted **first**) |
| `semantic/entities_graph.yml` | (6) entity graph | entities + typed relationships (join-path source of truth) |
| `knowledge/reference/` | (8) reference docs | LLM-facing domain docs (grain, hygiene filter, gotchas) |
| `knowledge/business_context/` | (5) business KB | glossary, initiatives, decision logs, org structure |
| `knowledge/query_corpus/` | (4) query corpus | curated NL→metric exemplars (**curate, don't raw-retrieve**) |
| `knowledge/lineage/` | (3) lineage | how the DAG is produced & used to rank tables |
| `.claude/skills/` | (3) skills | `analytics-router` (thin router) · `analytics-workflow` (process) · `sql-reviewer` (adversarial) |
| `mcp/` | distribution | serve the semantic layer + reference docs as MCP resources |
| `evals/` | (4) validation | gold questions + harness (per-domain ~90% gate + telemetry) |
| `governance/` | (4) governance | metric governance · provenance footer · tenant isolation |
| `.github/workflows/ci.yml` | (4) enforcement | paired-doc gate + dbt build + eval gate |

## Adapt it in 6 steps (minimum-viable-start)
1. Pick ~5 **canonical** datasets for ONE domain → fill `models/marts/`.
2. Write **one** reference doc (`knowledge/reference/<domain>.md`) + the **router skill**.
3. Write **a few dozen** evals (`evals/gold_questions.yml`).
4. Define the domain's **metrics** (`semantic/<domain>.yml`) — humans own the definitions.
5. Wire **colocation CI** (`.github/workflows/ci.yml`) + the **per-domain eval gate**.
6. Add the **workflow + adversarial** skills, then the **business-context KB**, then expose over **MCP**.

## Stack notes
Reference stack = **dbt + MetricFlow-style semantic layer + Claude Code Skills + MCP + CI**. Swap freely: warehouse → ClickHouse/Snowflake/BigQuery; semantic layer → Cube/LookML/Malloy; the *roles* are invariant. Pin tool versions at adoption.

> Rule that pays for itself: **generate documentation with Claude; humans own the metric definitions.** Auto-generating metric defs from raw tables encodes the very ambiguity you're trying to remove.
