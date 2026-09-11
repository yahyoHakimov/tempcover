#!/usr/bin/env bash
# TempCover — local runner
#   ./run.sh          start database + backend + frontend, seed admin, open the browser
#   ./run.sh stop     stop backend + frontend (database container is left running)
#   ./run.sh status   show what is running
#   ./run.sh logs     tail backend + frontend logs
#   ./run.sh reset    stop everything and delete the local database (fresh start)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
RUN_DIR="$ROOT/.run"
LOG_DIR="$ROOT/logs"

DB_CONTAINER="tempcover_db_dev"
DB_PORT=5434
API_PORT=8001
WEB_PORT=3001
ADMIN_USER="superadmin"
ADMIN_PASS="Admin12345!"

ORANGE='\033[38;5;202m'; GREEN='\033[0;32m'; DIM='\033[2m'; BOLD='\033[1m'; NC='\033[0m'
say()  { echo -e "${ORANGE}▸${NC} $*"; }
ok()   { echo -e "${GREEN}✔${NC} $*"; }
die()  { echo -e "\033[0;31m✖ $*${NC}" >&2; exit 1; }

port_open() { (echo > "/dev/tcp/127.0.0.1/$1") >/dev/null 2>&1; }
http_ok()   { curl -s -o /dev/null -w '%{http_code}' "$1" 2>/dev/null | grep -qE '^(200|307|401)$'; }

wait_for() { # wait_for <url> <label> <seconds>
  local i=0
  until http_ok "$1"; do
    i=$((i+1)); [ "$i" -ge "$3" ] && die "$2 did not start in time — see: ./run.sh logs"
    sleep 1
  done
}

pid_of_port() {
  if command -v lsof >/dev/null 2>&1; then lsof -ti "tcp:$1" -sTCP:LISTEN 2>/dev/null | head -1
  else ss -ltnp 2>/dev/null | awk -v p=":$1" '$4 ~ p"$" {print $NF}' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2
  fi
}

stop_one() { # stop_one <name> <port>
  local pid=""
  [ -f "$RUN_DIR/$1.pid" ] && pid="$(cat "$RUN_DIR/$1.pid")"
  [ -z "$pid" ] && pid="$(pid_of_port "$2" || true)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
    kill -9 "$pid" 2>/dev/null || true
    ok "$1 stopped"
  else
    echo -e "${DIM}  $1 was not running${NC}"
  fi
  rm -f "$RUN_DIR/$1.pid"
}

# ─────────────────────────────────────────────────────────────────────────────
cmd_stop() {
  say "Stopping TempCover"
  stop_one frontend "$WEB_PORT"
  stop_one backend  "$API_PORT"
}

cmd_status() {
  echo -e "${BOLD}TempCover — local status${NC}"
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$DB_CONTAINER"; then ok "database   running  (docker: $DB_CONTAINER, port $DB_PORT)"; else echo "  database   stopped"; fi
  if http_ok "http://127.0.0.1:$API_PORT/health"; then ok "backend    running  http://localhost:$API_PORT  (docs: /docs)"; else echo "  backend    stopped"; fi
  if http_ok "http://127.0.0.1:$WEB_PORT/admin/login"; then ok "frontend   running  http://localhost:$WEB_PORT"; else echo "  frontend   stopped"; fi
}

cmd_logs() {
  mkdir -p "$LOG_DIR"; touch "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
  tail -n 40 -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
}

cmd_reset() {
  cmd_stop
  say "Removing local database container"
  docker rm -f "$DB_CONTAINER" >/dev/null 2>&1 || true
  ok "Database removed — run ./run.sh to start fresh"
}

cmd_start() {
  mkdir -p "$RUN_DIR" "$LOG_DIR"
  command -v docker >/dev/null || die "Docker is required (for the local PostgreSQL)"
  command -v node   >/dev/null || die "Node.js 20+ is required"

  # 1. Database ---------------------------------------------------------------
  say "Database"
  if docker ps --format '{{.Names}}' | grep -qx "$DB_CONTAINER"; then
    ok "PostgreSQL already running ($DB_CONTAINER)"
  elif docker ps -a --format '{{.Names}}' | grep -qx "$DB_CONTAINER"; then
    docker start "$DB_CONTAINER" >/dev/null; ok "PostgreSQL started ($DB_CONTAINER)"
  else
    docker run -d --name "$DB_CONTAINER" \
      -e POSTGRES_USER=tempcover -e POSTGRES_PASSWORD=tempcover -e POSTGRES_DB=tempcover \
      -p "127.0.0.1:$DB_PORT:5432" postgres:17-alpine >/dev/null
    ok "PostgreSQL created ($DB_CONTAINER on port $DB_PORT)"
  fi
  for _ in $(seq 1 30); do docker exec "$DB_CONTAINER" pg_isready -U tempcover >/dev/null 2>&1 && break; sleep 1; done
  docker exec "$DB_CONTAINER" pg_isready -U tempcover >/dev/null 2>&1 || die "PostgreSQL is not accepting connections"

  # 2. Backend ----------------------------------------------------------------
  say "Backend"
  cd "$BACKEND"
  if [ ! -f .env ]; then
    cat > .env <<ENV
DATABASE_URL=postgresql://tempcover:tempcover@127.0.0.1:$DB_PORT/tempcover
SECRET_KEY=$(head -c 32 /dev/urandom | base64 | tr -d '\n=+/')
ENVIRONMENT=development
APP_URL=http://localhost:$WEB_PORT
CORS_ORIGINS=http://localhost:$WEB_PORT
STATIC_DIR=./static
BREVO_API_KEY=
SEED_SUPERADMIN_USERNAME=$ADMIN_USER
SEED_SUPERADMIN_PASSWORD=$ADMIN_PASS
ENV
    ok "Created backend/.env for local development"
  fi
  if [ ! -x .venv/bin/python ]; then
    if command -v uv >/dev/null; then uv venv --python 3.12 .venv -q; else python3 -m venv .venv; fi
    ok "Created Python virtualenv"
  fi
  if ! .venv/bin/python -c "import fastapi, weasyprint" >/dev/null 2>&1; then
    say "Installing Python dependencies (first run only)…"
    if command -v uv >/dev/null; then uv pip install -q --python .venv/bin/python -r requirements.txt
    else .venv/bin/pip install -q -r requirements.txt; fi
    ok "Python dependencies installed"
  fi
  .venv/bin/python seed.py | sed 's/^/    /'
  if http_ok "http://127.0.0.1:$API_PORT/health"; then
    ok "API already running on port $API_PORT"
  else
    nohup .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$API_PORT" --reload > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$RUN_DIR/backend.pid"
    wait_for "http://127.0.0.1:$API_PORT/health" "backend" 40
    ok "API running on http://localhost:$API_PORT"
  fi

  # 3. Frontend ---------------------------------------------------------------
  say "Frontend"
  cd "$FRONTEND"
  if [ ! -d node_modules ]; then
    say "Installing Node dependencies (first run only)…"
    npm ci --silent
    ok "Node dependencies installed"
  fi
  if http_ok "http://127.0.0.1:$WEB_PORT/admin/login"; then
    ok "Web app already running on port $WEB_PORT"
  else
    PORT="$WEB_PORT" nohup npx nuxt dev --port "$WEB_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$RUN_DIR/frontend.pid"
    wait_for "http://127.0.0.1:$WEB_PORT/admin/login" "frontend" 90
    ok "Web app running on http://localhost:$WEB_PORT"
  fi

  # 4. Done -------------------------------------------------------------------
  echo
  echo -e "${BOLD}${ORANGE}TempCover is running${NC}"
  echo -e "  Admin portal   ${BOLD}http://localhost:$WEB_PORT/admin/login${NC}"
  echo -e "  Driver portal  http://localhost:$WEB_PORT/driver/login"
  echo -e "  API docs       http://localhost:$API_PORT/docs"
  echo
  echo -e "  Super admin    ${BOLD}$ADMIN_USER${NC} / ${BOLD}$ADMIN_PASS${NC}"
  echo -e "  ${DIM}Create an agent under Agents → Add Agent, then sign in as the agent to see the dashboard.${NC}"
  echo -e "  ${DIM}Emails are printed to logs/backend.log (no BREVO_API_KEY set).${NC}"
  echo
  echo -e "  ${DIM}./run.sh stop · ./run.sh status · ./run.sh logs${NC}"

  local url="http://localhost:$WEB_PORT/admin/login"
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$url" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then open "$url" >/dev/null 2>&1 || true
  fi
}

case "${1:-start}" in
  start)  cmd_start ;;
  stop)   cmd_stop ;;
  status) cmd_status ;;
  logs)   cmd_logs ;;
  reset)  cmd_reset ;;
  *) echo "usage: ./run.sh [start|stop|status|logs|reset]"; exit 1 ;;
esac
