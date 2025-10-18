#!/usr/bin/env bash
set -euo pipefail

PGHOST="${POSTGRES_HOST:-postgres}"
PGPORT="${POSTGRES_PORT:-5432}"
PGUSER="${POSTGRES_USER:-admin}"
PGDB="${POSTGRES_DB:-ai_qa_platform}"
PGPASS="${POSTGRES_PASSWORD:-secure_password_123}"

export PGPASSWORD="$PGPASS"

echo "⏳ waiting for postgres at $PGHOST:$PGPORT..."

# Use Python to check connection instead of psql
python3 << PYTHON
import time
import psycopg2
import sys

for i in range(30):
    try:
        conn = psycopg2.connect(
            host="$PGHOST",
            port=$PGPORT,
            user="$PGUSER",
            password="$PGPASS",
            database="$PGDB"
        )
        conn.close()
        print("✅ postgres is ready")
        sys.exit(0)
    except Exception as e:
        if i < 29:
            time.sleep(2)
        else:
            print(f"❌ postgres connection failed: {e}")
            sys.exit(1)
PYTHON

# Run migrations using Python
python3 << PYTHON
import psycopg2

conn = psycopg2.connect(
    host="$PGHOST",
    port=$PGPORT,
    user="$PGUSER",
    password="$PGPASS",
    database="$PGDB"
)
cur = conn.cursor()

cur.execute("CREATE SCHEMA IF NOT EXISTS app;")

cur.execute("""
    CREATE TABLE IF NOT EXISTS app.sankalpa (
        id UUID PRIMARY KEY,
        text TEXT NOT NULL,
        context TEXT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
""")

cur.execute("""
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
""")

# Run the VCV table migration
cur.execute("""
    CREATE TABLE IF NOT EXISTS app.inference_capabilities (
        id UUID PRIMARY KEY,
        vcv_data JSONB NOT NULL,
        harvested_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
""")

conn.commit()
cur.close()
conn.close()

print("✅ migrations complete")
PYTHON

# Start FastAPI
echo "🚀 Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
