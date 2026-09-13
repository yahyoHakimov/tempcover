# TempCover

Short-term car insurance platform: a super admin manages agents, agents issue policies,
drivers receive their documents by email and view them in a self-service portal.

| Part      | Stack                                   | Folder      |
|-----------|-----------------------------------------|-------------|
| Frontend  | Nuxt 4, Pinia, Ubuntu font, orange UI   | `frontend/` |
| Backend   | FastAPI, SQLAlchemy, PostgreSQL, WeasyPrint PDFs, Brevo email | `backend/` |

## Routes

| URL | Who | What |
|-----|-----|------|
| `/admin/login` | agents & super admin | sign in |
| `/admin/dashboard/<username>` | agent | session countdown, Create Policy, policy lists |
| `/admin/policies`, `/admin/policies/create`, `/admin/policies/<id>` | agent | manage policies (PDFs, resend email, cancel) |
| `/admin/drivers` | agent | saved drivers |
| `/superadmin/**` | super admin | agents, all policies, drivers, static documents |
| `/driver/login` | driver | sign in with policy no. + surname + date of birth |
| `/verifydetailspolicy/complete/<policy no.>` | driver | policy details + documents (opened from the email link with `?t=<token>`, or after signing in) |
| `/` | — | redirects to `/driver/login` |

## Local development

Quickest way — one command starts the database (Docker), backend and frontend, seeds the super admin and opens the browser:

```bash
./run.sh            # start everything → http://localhost:3001/admin/login
./run.sh stop       # stop backend + frontend
./run.sh status     # what is running
./run.sh logs       # tail backend + frontend logs
./run.sh reset      # stop and delete the local database
```

Manual steps, if you prefer:

```bash
# 1. Database (any PostgreSQL 15+; this uses Docker on port 5434)
docker run -d --name tempcover_db_dev -e POSTGRES_USER=tempcover -e POSTGRES_PASSWORD=tempcover \
  -e POSTGRES_DB=tempcover -p 127.0.0.1:5434:5432 postgres:17-alpine

# 2. Backend
cd backend
cp .env.example .env            # then set DATABASE_URL=postgresql://tempcover:tempcover@127.0.0.1:5434/tempcover
                                #          APP_URL=http://localhost:3001, CORS_ORIGINS=http://localhost:3001,
                                #          SEED_SUPERADMIN_PASSWORD=<something>
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python seed.py        # creates the super admin + the internal "house" agent (idempotent)
.venv/bin/uvicorn app.main:app --reload --port 8001

# 3. Frontend (dev server proxies /api and /static to :8001)
cd ../frontend
npm ci
PORT=3001 npm run dev            # http://localhost:3001
```

Schema is managed with Alembic: `alembic upgrade head` (run.sh and the Docker image do this on start). With `BREVO_API_KEY` empty, emails are not sent —
the confirmation is printed to the backend log instead.

First login: `/admin/login` with `SEED_SUPERADMIN_USERNAME` / `SEED_SUPERADMIN_PASSWORD`, then
**Agents → Add Agent** to create an agent account (set an expiry date to drive the dashboard
countdown). Agents sign in on the same page.

## Policy lifecycle

| Event | What happens |
|---|---|
| Agent creates a policy | number `TCV-MOT-XXXXXXXX`; status `pending` if the start is in the future, else `active`; confirmation email with a one-click documents link |
| Start time reached | background job flips `pending → active` (every `LIFECYCLE_TICK_SECONDS`) |
| Agent edits dates/price/cover | mid-term adjustment: `version` +1, `reason_for_issue = MTA`, documents re-issued and emailed |
| 24 h before the end | driver gets an expiry reminder (once); agents get a daily digest of policies ending within 3 days |
| End time passed | `active → expired`; documents stay readable for the driver's records |
| Cancel (`POST /api/policies/{id}/cancel {reason}`) | status `cancelled` + reason + timestamp, driver emailed, documents and the link stop working |

Emails return `sent` / `skipped` / `failed`; only `sent` marks a policy as emailed. With `BREVO_API_KEY` empty everything is `skipped` and printed to `logs/backend.log`.

Documents (WeasyPrint from `backend/app/services/pdf_service/templates/`): Certificate of Motor Insurance, Policy Schedule, Statement of Fact — generated per policy; Policy Wording, IPID, contract etc. are uploaded once by the super admin under **Settings** and listed automatically.

## Configuration (`backend/.env`, see `.env.example`)

| Key | Purpose |
|-----|---------|
| `DATABASE_URL` | PostgreSQL DSN |
| `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT signing |
| `APP_URL` | public origin — used in emails and document links |
| `CORS_ORIGINS` | comma-separated allowed origins |
| `STATIC_DIR` | where uploaded static documents are stored (`/app/static` in Docker) |
| `BREVO_API_KEY`, `FROM_EMAIL`, `FROM_NAME`, `SUPPORT_EMAIL` | transactional email |
| `SEED_SUPERADMIN_*`, `HOUSE_TENANT_USERNAME` | first-run seed (`python seed.py`) |
| `TRADING_NAME`, `COMPANY_LEGAL_NAME`, `COMPANY_REG_NO`, `REGISTERED_OFFICE`, `FCA_FRN`, `UNDERWRITER_NAME`, `UNDERWRITER_FRN` | legal identity printed in email + PDF footers (blank = line omitted) |
| `POLICY_NUMBER_PREFIX` | default `TCV-MOT-` |
| `LIFECYCLE_TICK_SECONDS`, `REMINDER_HOURS_BEFORE_EXPIRY`, `AGENT_DIGEST_HOUR_UTC`, `AGENT_DIGEST_DAYS_AHEAD` | lifecycle jobs (0 disables) |

Frontend: `NUXT_PUBLIC_API_BASE` — leave empty in production (same-origin `/api`).

## Production (Docker, shared nginx gateway)

The stack runs at `/opt/tempcover` next to the other projects and is reached through the
server's shared nginx gateway over the external `proxy` Docker network.

```bash
# on the server, once
git clone <repo> /opt/tempcover && cd /opt/tempcover
cp backend/.env.example backend/.env && nano backend/.env     # real secrets, APP_URL=https://tempcover-verify.com
docker network inspect proxy >/dev/null 2>&1 || docker network create proxy
docker compose up -d
docker compose exec backend python seed.py

# gateway: add nginx/tempcover-verify.com.conf as a server block to the shared nginx.conf
#   (the swiftshield repo — commit it there, its deploys hard-reset the working tree),
#   issue the certificate first:
certbot certonly --webroot -w /var/www/letsencrypt -d tempcover-verify.com -d www.tempcover-verify.com
```

### Deploys

Push to `main` → GitHub Actions builds both images on the runner, pushes them to
`ghcr.io/yahyohakimov/tempcover-{backend,frontend}`, then SSHes in and runs
`git reset --hard` + `docker compose pull` + `up -d` (no builds on the server).
Required repository secrets: `DO_HOST`, `DO_USERNAME`, `DO_SSH_KEY`.
`backend/.env` on the server is preserved across deploys by the workflow.

## Branding

Logo PNGs live in `frontend/public/` (web + emails; the confirmation email uses
`tempcover-logo-dark.png` and `trustpilot.png`, both taken from the original Tempcover email) and
`backend/app/services/pdf_service/signatures/` (PDFs). Colours are CSS variables in
`frontend/app/assets/css/main.css` (`--brand-500: #FF5100`).
