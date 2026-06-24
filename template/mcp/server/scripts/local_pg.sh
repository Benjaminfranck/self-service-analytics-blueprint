#!/usr/bin/env bash
# No-Docker local Postgres for the demo (uses initdb/pg_ctl from a local Postgres install).
#   bash scripts/local_pg.sh up     # init + start + load schema/seed; prints WAREHOUSE_DSN
#   bash scripts/local_pg.sh stop    # stop the cluster
set -euo pipefail

SERVER_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PGDATA_DIR="${PGDATA_DIR:-$SERVER_DIR/.pgdata}"
PGPORT="${PGPORT:-55432}"
DSN="postgresql://postgres@localhost:${PGPORT}/analytics"

cmd="${1:-up}"
case "$cmd" in
  up)
    if [ ! -d "$PGDATA_DIR" ]; then
      initdb -D "$PGDATA_DIR" --auth=trust -U postgres >/dev/null
    fi
    pg_ctl -D "$PGDATA_DIR" -o "-p ${PGPORT} -k /tmp" -l "$PGDATA_DIR/server.log" -w start
    createdb -h localhost -p "$PGPORT" -U postgres analytics 2>/dev/null || true
    psql -h localhost -p "$PGPORT" -U postgres -d analytics -v ON_ERROR_STOP=1 -q -f "$SERVER_DIR/schema.sql"
    psql -h localhost -p "$PGPORT" -U postgres -d analytics -v ON_ERROR_STOP=1 -q -f "$SERVER_DIR/seed.sql"
    echo "READY."
    echo "export WAREHOUSE_DSN=${DSN}"
    ;;
  stop)
    pg_ctl -D "$PGDATA_DIR" -w stop || true
    ;;
  *)
    echo "usage: $0 [up|stop]"; exit 1 ;;
esac
