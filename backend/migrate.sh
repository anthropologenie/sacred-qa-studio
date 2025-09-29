# backend/migrate.sh
#!/usr/bin/env bash
set -euo pipefail

PGHOST="${POSTGRES_HOST:-postgres}"
PGPORT="${POSTGRES_PORT:-5432}"
PGUSER="${POSTGRES_USER:-admin}"
PGDB="${POSTGRES_DB:-ai_qa_platform}"
PGPASS="${POSTGRES_PASSWORD:-secure_password_123}"

export PGPASSWORD="$PGPASS"

echo "⏳ waiting for postgres at $PGHOST:$PGPORT..."
until psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" -c "select 1" >/dev/null 2>&1; do
  sleep 2
done
echo "✅ postgres is ready"

psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" -v ON_ERROR_STOP=1 <<'SQL'
CREATE SCHEMA IF NOT EXISTS app;
CREATE TABLE IF NOT EXISTS app.sankalpa (
  id UUID PRIMARY KEY,
  text TEXT NOT NULL,
  context TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS app.qa_logs (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  agent_id TEXT NOT NULL,
  model TEXT NULL,
  device TEXT NULL,
  quant TEXT NULL,
  request_json JSONB NULL,
  response_json JSONB NULL
);
SQL

echo "✅ migrations complete"

