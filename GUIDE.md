# Self-Service Data Analytics — Framework & Reusable Blueprint

> A reusable framework I developed for **governed, AI-ready self-service analytics** in my data-product work: the architecture, the runtime, and a copyable repo scaffold (`./template/`) for **AI-driven, natural-language analytics on any data warehouse** — built governance-first so the answers are trustworthy. The worked example is security-flavored (vuln findings + assets); repoint the `<placeholders>` at any domain. Stack-agnostic in shape; the concrete files use **dbt + a semantic layer + Claude Code Skills + MCP + an eval harness + CI**, with alternatives noted inline.
---

## 0. How to use this
- **`GUIDE.md`** (this file) = the principle, the architecture, how it runs, the components, and a phased rollout.
- **`./template/`** = a real, adaptable repo scaffold — one directory per concept (semantic layer, lineage, entity graph, query corpus, business context, skills, evals, governance, CI, MCP). Copy it, repoint the placeholders at your domain/warehouse, and you have the skeleton of a production system.
- Stack-agnostic in shape; swap any layer (ClickHouse, Cube, LookML, Snowflake) — the *roles* are what matter.

---

## 1. The principle — "Analytics isn't software"
In code there are many right answers and tests catch the wrong ones. In analytics there's usually **one** right answer and no test proves it. So the whole job reduces to one capability: **map a question to the right *governed* entity and metric.** Get that right and the resulting SQL is trivial; get it wrong and you ship a confident, plausible, **wrong** number that nobody questions.

> **The model is rarely the bottleneck — the governed context layer is.**

So this framework stops trying to make the LLM smarter and instead makes the **context** unambiguous: canonical data, a semantic layer the agent must consult first, skills that route it to the right place, and a validation loop that proves the answer. On sensitive data (security, finance, health) the bar isn't "a chart" — it's **"an answer you can act on without being misled."** A plausible-but-wrong *"0 critical exposures"* isn't a bad chart; it's a missed breach.

**The throughline:** *win at the modeled-data layer; once the question maps to the right governed entity and metric, the SQL writes itself.*

---

## 2. The architecture — four stacked layers
```
+----------------------------------------------------------------------+
|  (4) VALIDATION    offline evals - per-domain accuracy gate - ablation|
|                    adversarial-review sub-agent - provenance footer   |
|                    passive monitoring (semantic-layer-use %, corrections)|
+----------------------------------------------------------------------+
|  (3) SKILLS        knowledge skill (thin router) + workflow ("unbook")|
|     (procedural)   skill + adversarial reviewer - served via MCP      |
+----------------------------------------------------------------------+
|  (2) SOURCES OF TRUTH (declarative - what the agent consults)         |
|   - Semantic layer  (compiled metric/dimension defs - consulted FIRST)|
|   - Lineage / transformation graph (which model feeds what; freshness)|
|   - Query corpus    (historical SQL - CURATED into refs, not read raw)|
|   - Business-context KB (glossary, initiatives, decision logs, org)   |
+----------------------------------------------------------------------+
|  (1) DATA FOUNDATIONS  canonical, owned, consumption-ready datasets   |
|                        (dimensional models) - metadata as a product   |
|                        - enforced by tooling + CI + mandate           |
+----------------------------------------------------------------------+
        sources -> warehouse -> dbt transforms -> (layers above) -> NL query - dashboards
```
**The order is the lesson:** *start at the bottom.* A handful of canonical datasets, a few dozen evals, and a thin knowledge skill capture most of the value before anything fancy.

---

## 3. How it works — a question's journey
A user asks, in plain language: *"How many open critical findings are on internet-facing assets, by team, last 30 days?"* (security is the example domain — the flow is identical for "weekly active accounts by plan," etc.)

1. **Router skill loads** — carries must-know context + the workflow, and **narrows the search space** from a million fields to ~30 curated reference files for this domain.
2. **Semantic layer FIRST (required).** Map the question to a *governed metric* — `open_critical_findings` sliced by `team` over 30 days. The agent picks the **metric + dimensions + filters**; it never writes the SQL — so it **can't express a wrong join or aggregation.**
3. **Fallback to reference docs** only if no metric covers it; the **lineage graph** turns "I don't know the metric" into "I know which governed model to aggregate from."
4. **Entity graph** supplies the join path so no join is hallucinated.
5. **Execute read-only**, EXPLAIN/dry-run first, on the right performance tier.
6. **Adversarial review sub-agent** challenges assumptions before the answer ships. Blocking findings fixed and re-reviewed — no self-certifying.
7. **Answer + provenance footer**: `Source: semantic layer · Freshness: <max date> · Owner: <team> · Reviewed: ✓ round 1`.
8. **Passive monitoring** records semantic-layer-resolution % + correction language; a correction-harvester drafts a one-line reference-doc fix and opens a PR.

---

## 3b. How it runs — and what the MCP actually serves
**The folder is not an app you run — it's the *governed source of truth*.** Two clocks:
- **Build-time (the repo):** dbt models, semantic/metric definitions, entity graph, reference docs, business context, evals, governance, ADRs, CI. These change via PR, CI gates them, merge publishes. *Nothing here is a running service.*
- **Runtime:** a **thin MCP server** exposes the governed layer to the agent; the **skills** load into the agent; the agent runs **read-only** against the warehouse and attaches a provenance footer.

**Is it an MCP? Not on its own — it's *exposed over* MCP.** And critically, **the MCP does not take a raw SQL string and run it.** That would be text-to-SQL, with all its hallucinated-join risk. Instead it serves **governed, semantic operations** (`mcp/mcp.config.json`):

| Tool | Agent sends | MCP returns |
|---|---|---|
| `list_metrics` | (nothing) | the governed **metric catalog** (names, dimensions, owner, tier) — *metadata* |
| `compile_metric` | a **structured request** `{metric, dimensions, filters, grain}` — *not SQL* | the server **compiles it to SQL, runs it read-only**, returns **rows + the generated SQL (as provenance) + freshness** |
| `resolve_entity` | a noun | the entity + its **join paths** from the graph — *metadata* |
| `get_reference_doc` | a domain | the **reference doc** — *text* |
| `source_freshness` | a source | **max date + freshness** — *metadata* |
| `rank_tables` / `lineage` | a question / model | **table ranking** / **lineage** — *metadata* |

So the MCP serves **(a) metadata** that grounds the agent, **(b) data** via `compile_metric` (the agent chooses a metric; the *server* generates and runs the SQL), and **(c) the generated SQL back as a provenance artifact** (show-your-work), never as an input. **That boundary is where governance lives** — the agent selects from governed metrics/entities, so it can only reference legitimate objects. *(Exception: when no metric covers a question, a constrained raw-SQL fallback is allowed — restricted to entity-graph joins, read-only, forced through the adversarial reviewer, and logged so you add the missing metric. It's the last resort, not the path.)* Swap MCP for another transport and the framework still stands — the governance is the point.

> **Runnable:** a reference server in `template/mcp/server/` implements this against **Postgres** — a governed request compiles to read-only SQL and returns rows + the generated SQL + freshness, with **tenant isolation** and **fails-closed** behavior you can run locally (`docker compose up` → `python demo.py`).

---

## 4. The components (what / why / how — each maps to a `template/` file)

### (1) Canonical datasets & data foundations → `template/models/`
Collapse ambiguity **upstream of the agent**: if *"critical finding"* resolves to **one** governed dataset instead of forty candidates, the hardest failure (concept↔entity ambiguity) disappears before the agent searches. Dimensional models; **metadata as a first-class product** (descriptions, grain, ranges, ownership, tiering); deprecate near-duplicates. Mark `meta: {canonical: true, certified: true}`.

### (2) Semantic layer (consulted first) → `template/semantic/findings.yml`
Compiled **metric + dimension definitions** the agent is *required* to try first. The win: if it picks the right metric and dimensions, **the query is correct by construction** — it **fails closed** (an error) rather than open (a plausible-wrong number).
- **Additivity is correctness-critical:** *additive* (sum/count — roll up freely), *semi-additive* (balances — snapshot, don't sum over time), *non-additive* (distinct counts, ratios — recompute; `distinct(A∪B) ≠ distinct(A)+distinct(B)`). Distinct counts need **HLL sketches** or **symmetric aggregates** to survive rollups/fan-out.
- **House rule:** **generate docs with the LLM; humans own the metric definitions.** Auto-generating definitions from raw tables just encodes the ambiguity you're trying to remove.

### (3) Lineage / transformation graph → `template/knowledge/lineage/`
The dependency DAG (dbt `manifest.json` / OpenLineage). Two jobs: **rank/choose tables** (downstream-reference count, centrality, prefer `marts` + certified) and feed **freshness & provenance** on the footer. Column-level lineage gives column-level provenance.

### (4) Query corpus → `template/knowledge/query_corpus/`
Historical SQL. **The counter-intuitive rule:** dumping past queries at the agent barely helps — *structure beats access*; it sees the right precedent and still doesn't use it. So **treat the corpus as raw material to CURATE into structured reference docs + reusable analysis patterns — not as a source the agent reads raw.** When you use exemplars, retrieve by **masked-skeleton** similarity and store `metric_request` targets, not raw SQL.

### (5) Business-context knowledge base → `template/knowledge/business_context/`
An agent that doesn't understand the business answers what was asked, not what was meant. A KB of glossary terms, **initiatives** (so *"the Q2 hardening push"* resolves to a program + its metrics), **decision logs** (ADRs), and **org structure**. **Critical rule: store metric *IDs*, never live metric *values*** — resolve numbers through the semantic layer at answer time so nothing goes stale.

### (6) Entity / relationship graph → `template/semantic/entities_graph.yml`
Models the **business domain, not storage**: entities + typed relationships with cardinality. Three jobs for NL: entity resolution (noun→entity), **join-path selection** (so joins aren't hallucinated), and disambiguation.

### (7) Skills (procedural) → `template/.claude/skills/`
Markdown folders; only `description` loads up front, body loads **on demand** (progressive disclosure); keep `SKILL.md` < 500 lines. **Knowledge skill** (`analytics-router`) = the thin router (must-know context → ~30 reference files); **workflow/"unbook" skill** (`analytics-workflow`) = the senior-analyst process (clarify → find → query → adversarial review → report) + reusable patterns; **adversarial reviewer** (`sql-reviewer`) = a sub-agent that challenges assumptions, **no self-certify**. **Distribution:** authored once, served everywhere (IDE plugin marketplace, cloud blobs, and **MCP resources**) — same answer in every surface.

### (8) Reference docs written for the LLM → `template/knowledge/reference/findings.md`
For agents, not humans. Consistent markdown: Business Context → Entity Grain → Standard Hygiene Filter → Dimensions → Key Tables → **Gotchas** → Best Practices/Query Patterns → **Routing triggers** → Cross-References.

### (9) Validation → `template/evals/` + `template/governance/provenance_footer.md`
- **Offline evals**: Q/A pairs (dashboard + long-tail; LLM-generated then human-validated; harvested from corrections). **Anchor ground truth** (pin to a snapshot *or* grade the agent's **query**, not its number). Store every run as **telemetry** (skill version, git SHA, model, pass/fail, tokens, latency).
- **Per-domain gate** (~90%) before a domain "goes live." **Ablation** (hold evals fixed, change one component); keep a **negative-results list**.
- **Provenance footer** on every answer; **passive monitoring** of semantic-layer-use % + correction language.

### (10) Governance, colocation & CI → `template/governance/`, `template/.github/workflows/ci.yml`
Governance needs **teeth or it decays**: **tooling** + **CI** + **mandate**. **Colocate** everything in one repo so it moves in lockstep — and a **CI hook fails a PR that changes a reporting model without touching its reference/skill doc.** Multi-tenant: tenant isolation as a governed, enforced control.

---

## 5. The reusable repo scaffold (`./template/`)
```
template/
  README.md                       how to adapt; minimum-viable-start
  dbt_project.yml                 transform layer (swap warehouse)
  models/{staging,marts}/         (1) canonical datasets + contracts/owner/meta
  semantic/findings.yml           (2) semantic layer — metrics + additivity
  semantic/entities_graph.yml     (6) entity/relationship graph + worked NL->SQL
  knowledge/reference/*.md         (8) LLM-facing reference docs (findings · assets · risk)
  knowledge/business_context/     (5) glossary - initiatives/ - decisions/ - org.md
  knowledge/query_corpus/         (4) corpus.jsonl + README (curate, don't raw-retrieve)
  knowledge/lineage/README.md     (3) how lineage is produced + table ranking
  .claude/skills/                 (7) analytics-router - analytics-workflow - sql-reviewer
  mcp/                            serve semantic layer/catalog as MCP resources (see §3b)
  mcp/server/                     ⭐ RUNNABLE reference server (Postgres): engine + MCP + demo + tests
  evals/                          gold_questions.yml - run_evals.py (gate+telemetry) - README
  governance/                     metric_governance.md - provenance_footer.md - tenant_isolation.md
  docs/adr/                       0001-text-to-metric-not-text-to-sql.md
  .github/workflows/ci.yml        paired-doc gate + dbt build + eval gate + publish-on-merge
```

---

## 6. Phased rollout (minimum-viable-start first)
1. **Foundations (wk 1–2).** ~5 canonical datasets for ONE domain + descriptions/tests/owner. A thin **knowledge/router skill** + one reference doc. **A few dozen evals.** *Most of the value.* Gotcha: one domain, don't boil the ocean.
2. **Semantic layer (wk 3–4).** Define the domain's metrics/dimensions (humans own defs); router requires it first; additivity-correct distinct counts. Gotcha: get additivity right or dashboards are confidently wrong.
3. **Workflow skill + adversarial review (wk 4–5).** Encode clarify→find→query→review→report; add the reviewer. Gotcha: it costs tokens/latency — gate it to higher-stakes answers if needed.
4. **Governance + colocation + CI (wk 5–6).** One repo; paired-doc CI hook; per-domain gate; provenance footer. Gotcha: governance without enforcement decays.
5. **Business-context KB (wk 6+).** Glossary, initiatives, decision logs, org; contextual retrieval. Gotcha: store metric IDs, never values.
6. **NL UX + MCP distribution (ongoing).** Expose the semantic layer + reference docs over MCP; ship NL to one domain behind the eval gate; turn on passive monitoring + correction harvesting. Expand domain by domain.

---

## 7. Adapting it to a domain
The framework is domain-agnostic; the repo just ships **one worked example** (security: findings + assets). To repoint it:
- Replace `models/marts/*` with your canonical facts/dims and `_schema.yml` (grain, contracts, owner, certified/canonical).
- Define your metrics in `semantic/<domain>.yml` (mind additivity) and your entities/joins in `entities_graph.yml`.
- Write one `knowledge/reference/<domain>.md` and seed `business_context/` (glossary → metric IDs, initiatives, decisions, org).
- Point the router skill at your reference docs; write a few dozen `evals/gold_questions.yml`.
- Everything else (skills shape, MCP tools, governance, provenance footer, CI hook) is reusable as-is.

## 8. Questions to ask before building
1. How important is a correct answer **today** vs. as models improve? (don't over-build for gaps models will close)
2. How will your **business complexity** change?
3. How **technical** is the audience? (data scientists catch errors; an exec doesn't)
4. How much will you **pay for accuracy**? (an adversarial-review pass costs tokens + latency)
5. What are your **access-control / privacy** constraints? (decides *one agent or many scoped ones*)

Design against the **three failure modes**: concept↔entity ambiguity (→ canonical datasets + semantic layer), staleness (→ colocation + CI + auto-sync), retrieval failure (→ the router narrowing to ~30 files).

## 9. Why it holds up
Swap any layer — warehouse, semantic engine, BI tool, even MCP for another transport — and the framework still stands, because the **roles** are what matter, not the tools. It scales by adding **governed domains**, not by making the model bigger. The whole bet is simple: **win at the modeled-data layer, and trustworthy self-service analytics — dashboards and natural language alike — follows.**
