# Reference MCP server — runnable end-to-end (Postgres)

A small, **runnable** implementation of the MCP layer described in [`../README.md`](../README.md) and
[`../../../GUIDE.md`](../../../GUIDE.md), wired to a real Postgres. It proves the blueprint's core claim:
a governed metric request becomes read-only SQL, runs against the warehouse, and comes back with rows +
the generated SQL + freshness — **the agent never writes SQL and never sees credentials.**

![End-to-end demo: a governed request compiles to read-only SQL and returns rows + provenance, with tenant isolation, read-only enforcement, and fails-closed behavior](./demo.svg)

> **Scope:** `engine.py` is a *reference compiler* for the example security metrics in
> [`../../semantic/findings.yml`](../../semantic/findings.yml). For production, swap in the dbt Semantic
> Layer / MetricFlow or Cube — the governance properties (text-to-metric, read-only, tenant-injected,
> fails-closed) are the point, not this particular compiler.

## What's here
| File | Role |
|---|---|
| `engine.py` | Registry compiler (`build_sql`/`compile_metric`) + read-only Postgres execution + tenant injection + fails-closed errors. |
| `server.py` | MCP stdio server (`mcp` SDK) exposing `list_metrics`, `compile_metric`, `resolve_entity`, `get_reference_doc`, `source_freshness`. |
| `demo.py` | No-client CLI — prints rows + compiled SQL + provenance footer for 4 questions, then a fails-closed example. |
| `schema.sql` / `seed.sql` | Synthetic marts (with a `tenant` column) + seed data for two tenants. |
| `docker-compose.yml` | One-command Postgres (auto-loads schema + seed). |
| `scripts/local_pg.sh` | No-Docker path via `initdb`/`pg_ctl`. |

## Run it (Docker — portable)
```bash
cd template/mcp/server
docker compose up -d
pip install -r requirements.txt
WAREHOUSE_DSN=postgresql://postgres:postgres@localhost:5432/analytics DEMO_TENANT=acme python demo.py
```

## Run it (no Docker)
```bash
cd template/mcp/server
pip install -r requirements.txt
bash scripts/local_pg.sh up        # prints the WAREHOUSE_DSN to export
export WAREHOUSE_DSN=postgresql://postgres@localhost:55432/analytics DEMO_TENANT=acme
python demo.py
bash scripts/local_pg.sh stop      # when done
```

## As an MCP server
Point your MCP client at `python server/server.py` (see [`../mcp.config.json`](../mcp.config.json)). The
server reads `WAREHOUSE_DSN`, `DEMO_TENANT`, and `STATEMENT_TIMEOUT_MS` from the environment.

## Tests

The compiler's governance guarantees are unit-tested (no database needed):

```bash
pip install pytest && pytest template/mcp/server/tests -q   # 9 passed
```

They assert the tenant predicate is always injected, only allowlisted metrics/dimensions/filters
compile (a raw-SQL/injection attempt is rejected), and unknown objects fail closed. CI runs them on every push.

## Security properties (enforced, not just documented)
- **Read-only:** connect as a least-privilege role *and* `SET default_transaction_read_only = on`; a
  `statement_timeout` bounds runaway queries.
- **Tenant isolation:** the `WHERE tenant = %(tenant)s` predicate is injected from `DEMO_TENANT`/session —
  `compile_metric` has no tenant parameter, so the agent cannot widen scope.
- **No raw SQL from the request:** the compiler emits SELECT only over allowlisted metrics/dimensions/
  filters; values are parameterized.
- **Fails closed:** an unknown metric/dimension/filter returns an error + suggestions, never a guess.

Try it: `DEMO_TENANT=globex python demo.py` returns a *different* count than `acme` (isolation works);
asking for a non-existent metric returns the fails-closed error.
