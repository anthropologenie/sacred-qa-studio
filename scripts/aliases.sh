
alias dcu='docker-compose --env-file .env.local.compose up -d'
alias dco='docker-compose --env-file .env.local.compose -f docker-compose.yml -f docker-compose.override.yml up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f --tail=200'
alias migrate='cd backend && ./migrate.sh'
alias api='cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
alias web='pnpm -C apps/web dev'
