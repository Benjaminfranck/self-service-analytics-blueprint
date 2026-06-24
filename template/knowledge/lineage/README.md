# ③ Lineage / transformation graph

The dependency DAG of every model. Produced automatically; consumed by the agent for **table
choice** and **provenance**.

## How it's produced
- **dbt**: built at parse time from `{{ ref() }}` / `{{ source() }}` calls → `target/manifest.json`
  (nodes, sources, exposures, `parent_map`/`child_map`). Cheapest place for the agent to read lineage.
- **Column-level lineage**: dbt Explorer (Enterprise) or SQLGlot AST parsing → column→column provenance.
- **OpenLineage** (optional, cross-tool): run `dbt-ol run` (the `openlineage-dbt` wrapper) → emits
  Run/Job/Dataset events with a `columnLineage` facet to a store like Marquez.

## How the agent uses it
1. **Table ranking / choice.** Score candidates by: downstream-reference count (`len(child_map)` +
   exposures), DAG centrality, layer (prefer `marts` over `staging`), and `meta.certified/canonical`.
   → a "findings" question routes to certified `fct_findings`, never a staging view.
2. **Freshness & provenance.** `dbt source freshness` (compares `loaded_at_field` to thresholds)
   feeds the **Freshness** field on the provenance footer; lineage feeds the **Source/Owner** fields.
3. **Impact analysis (for CI).** A model change → walk `child_map` to find affected dashboards
   (exposures) and reference docs → the paired-doc CI gate fires if docs weren't updated.

> The lineage graph turns "I don't know the metric" into "I know which governed model to aggregate from."
