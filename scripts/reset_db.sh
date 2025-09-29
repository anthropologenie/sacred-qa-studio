#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Sacred-QA-Studio DB Reset Tool
# - Stops stack
# - Removes ONLY the Postgres volume
# - Restarts stack (CPU override friendly)
# - Applies Alembic migrations from backend venv
# -----------------------------

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.override.yml"
ENV_FILE=".env.local.compose"
PG_VOL_NAME="sacred-qa-studio_pgdata"
BACKEND_DIR="backend"

echo "⚠️  WARNING: This will ERASE Postgres data in volume: ${PG_VOL_NAME}"
read -p "Type 'RESET' to continue: " CONFIRM
if [ "$CONFIRM" != "RESET" ]; then
  echo "Aborted."
  exit 1
fi

echo "🛑 Stopping containers..."
docker compose ${COMPOSE_FILES} down

echo "🧹 Removing Postgres volume: ${PG_VOL_NAME}"
docker volume rm -f "${PG_VOL_NAME}" || true

echo "🚀 Starting core stack (with override if present)..."
if [ -f ".env.local.compose" ]; then
  docker compose --env-file "${ENV_FILE}" ${COMPOSE_FILES} up -d
else
  docker compose ${COMPOSE_FILES} up -d
fi

echo "⏳ Waiting for Postgres to become healthy..."
# Basic wait loop
for i in {1..30}; do
  if docker exec -it sacred-qa-studio-postgres-1 pg_isready -U admin -d ai_qa_platform >/dev/null 2>&1; then
    echo "✅ Postgres is ready."
    break
  fi
  sleep 2
done

echo "🔐 Preparing backend env for Alembic..."
pushd "${BACKEND_DIR}" >/dev/null

# Ensure venv present
if [ ! -d ".venv" ]; then
  echo "📦 Creating backend virtualenv..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# Ensure deps installed
pip install -r requirements.txt >/dev/null

# Ensure local env exists
if [ ! -f ".env.local.backend" ]; then
  cat > .env.local.backend <<'EOF'
DATABASE_URL=postgresql://admin:secure_password_123@localhost:5432/ai_qa_platform
VALKEY_URL=redis://localhost:6379/0
AI_SERVICE_URL=http://localhost:8001
SECRET_KEY=your_secret_key_here
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
  echo "📝 Created backend/.env.local.backend with default values."
fi

# Export env vars for current shell
export $(grep -v '^#' .env.local.backend | xargs)

echo "🏗️  Running Alembic migrations..."
# Create empty baseline if no versions exist
if [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
  alembic revision -m "baseline" >/dev/null
fi
alembic upgrade head

deactivate
popd >/dev/null

echo "🎉 Reset complete. DB is clean and migrated."
echo "➡️  Next:"
echo "  - Backend (local): cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  - Frontend:        pnpm -C apps/web dev"
echo "  - Inference:       http://localhost:8001/health"
