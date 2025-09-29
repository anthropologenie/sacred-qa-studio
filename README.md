
# sacred-qa-studio (MVP)

Hybrid workspace with Next.js (UI), FastAPI (API), ONNX (CPU-only inference by default), Postgres, Valkey.
Use `docker-compose.override.yml` for laptop mode.

## Quickstart (WSL)
```bash
cd ~/projects
unzip sacred-qa-studio-full.zip -d sacred-qa-studio
cd sacred-qa-studio

# Husky + commit template
git init
git config commit.template .gitmessage.txt

# Laptop lightweight stack
docker-compose --env-file .env.local.compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Backend migrations (runs Alembic + starts API if local)
cd backend && ./migrate.sh
```
