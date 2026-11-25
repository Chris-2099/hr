# HR Workforce & Org Health Dashboard — API + Pipeline

A FastAPI backend for the dashboard described in the `HR_Workforce_OrgHealth
Dashboard Charter`, backed by SQLite, serving a real web application (the
frontend lives in `frontend/`, rebuilt separately from this backend work).
The backend's job: enforce RBAC, serve HR/recruiting data over HTTP, and
pull from Jobvite (ATS) + Dayforce (HRIS) to keep the database current.
A Power BI CSV export path also still exists (`src/export_powerbi.py`) for
anyone who wants to point Power BI at the same data independently of the
web app.

The dashboards still run on fake data shaped like a real Jobvite/Dayforce
feed. **Real, working Jobvite/Dayforce API client code exists** (see "API
integrations" below) and makes genuine calls to those real services — it
just has no real credentials yet, so every call fails cleanly and logs the
attempt rather than silently doing nothing.

> This branch's `backend/src/` layout (`api/clients/`, `api/routers/`,
> `core/`, `utils/`) mirrors the structure of this repo's `main` branch, an
> earlier Supabase/FastAPI attempt at the same charter — kept similar so the
> two are easy to compare/copy between. Two deliberate differences remain:
> SQLite instead of Supabase (self-contained, nothing to provision), and a
> from-scratch RBAC/auth layer (`main` never had one).
>
> File-organization rule followed throughout: group by source system or by
> cohesive serving concern (`api/jobvite.py`, `api/dayforce.py`,
> `api/routers/employees.py` for Dayforce-shaped data, `api/routers/recruiting.py`
> for Jobvite-shaped data) — never one file per individual table/concept
> (no `employee_movements.py`-style sprawl).

## What's here

- **`backend/src/seed/seed_data.py`** — generates ~300 employees, ~2,000+
  recruiting/performance/engagement/compensation records, plus demo login
  users, into `backend/hr_dashboard.db` (SQLite). Fixed random seed —
  re-running it reproduces the same dataset byte-for-byte.
- **`backend/src/main.py`** — the FastAPI app: CORS, router registration,
  `/health`.
- **`backend/src/api/routers/`** — the serving layer:
  - `auth.py` — login (`POST /api/auth/login`) + `GET /api/auth/me`.
  - `employees.py` — Dayforce-shaped reads (`/api/departments`,
    `/api/employees`), RBAC-filtered.
  - `recruiting.py` — Jobvite-shaped reads (`/api/requisitions`,
    `/api/candidates`, `/api/applications`), RBAC-filtered.
  - `dashboard.py` — cross-cutting summary metrics (`/api/dashboard/summary`).
  - `admin.py` — user management, admin-only.
  - `integrations.py` — admin-only routes that trigger the pipeline below
    over HTTP instead of the CLI (same functions either way).
- **`backend/src/api/jobvite.py`** / **`backend/src/api/dayforce.py`** — the
  real ingestion pipeline, one module per source system: each calls its
  client (`src/api/clients/*_client.py`), maps the response onto our schema
  (`src/api/clients/*_mapper.py`), and upserts into the database. Logs
  every attempt (success or failure) to the `ingestion_runs` table.
  Runnable standalone (`python -m src.api.jobvite`) or via
  `POST /api/integrations/jobvite/sync/...` — same code, two ways to invoke it.
- **`backend/src/export_powerbi.py`** — reads every table out of the
  database into a pandas DataFrame and writes one CSV per table, for
  anyone pointing Power BI at this data independently of the web app.

## Quick start (local)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # defaults work as-is for local dev
python -m src.seed.seed_data     # (re)creates hr_dashboard.db with fresh fake data
uvicorn src.main:app --reload --port 8000

# Frontend (separate terminal, see frontend/ once rebuilt)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

**Login is disabled by default for easier local testing**
(`DISABLE_AUTH=true` in `backend/.env.example`) — hitting any endpoint
auto-authenticates you as the seeded `admin` user, and an
`X-Dev-User-Email` header lets you impersonate any other seeded user to
exercise RBAC without a login screen. This is a backend-only flag
(`src/core/config.py` / `src/core/deps.py:get_current_user`); the real
login flow and all role/department enforcement underneath it are
unchanged and fully testable this way — **set `DISABLE_AUTH=false`**
before any real deployment (already the default in `docker-compose.yaml`).

Seeded demo accounts (see `DEMO_USERS` in `seed_data.py`; password
`password` for all): `admin`, `admin@admin` (both `admin` role). Use
`POST /api/admin/users` to create accounts for the other roles
(`executive`, `hr_business_partner`, `recruiter`, `viewer`) as needed.

To pull real data instead of/alongside the demo seed: run
`python -m src.api.jobvite` / `python -m src.api.dayforce` (or trigger the
same via `POST /api/integrations/...` once logged in as an admin).

## Docker

```bash
docker compose up --build
```

Seeds the DB into a named volume on first boot only, then serves the API
on `http://localhost:8000` (the frontend container, once added, will proxy
through it). Set `SECRET_KEY` in a `.env` file at the repo root before any
real deployment — the default is a dev placeholder. Ingestion and the
Power BI CSV export are separate, on-demand steps, not part of container
startup — run them via `docker compose run --rm backend python -m src.api.jobvite`
(etc.) or a cron entry.

## Data model

Two source-system-shaped halves, joined on `department_id` / `employee_id`.
See `backend/src/models.py` for the full schema (every Jobvite/Dayforce
field mapping is called out in an inline comment next to its column).

- **Dayforce-shaped (HRIS):** `employees`, `departments`, `positions`,
  `locations`, `compensation`, `performance_reviews`, `pto_usage`,
  `employee_relations_cases`, `engagement_surveys` /
  `engagement_responses`, `succession_plans`, `training_completions`,
  `workforce_plans`. Dayforce's REST API identifies every resource by a
  customer-assigned, stable `XRefCode` rather than an internal numeric id;
  `departments.dayforce_xref_code`, `locations.dayforce_xref_code`,
  `positions.dayforce_xref_code`, and `employees.dayforce_employee_id` hold
  that value so a real sync can upsert on it directly instead of needing a
  remap. Dayforce keeps department/position/location/manager on an
  effective-dated `WorkAssignments` subordinate resource per employee; this
  build keeps only the *current* assignment on `employees` (documented in
  `models.py`'s `Employee` docstring) — a real integration wanting exact
  historical org charts would need a `WorkAssignment` history table, which
  is out of scope here.
- **Jobvite-shaped (ATS):** `requisitions`, `candidates`, `applications`,
  `interviews`, plus a thin `departments.jobvite_id` sync (`src/api/jobvite.py:sync_departments`
  matches Jobvite's `/department` taxonomy to an existing department by
  name — Jobvite's response doesn't carry enough to create a department on
  its own). Field names and types follow the Jobvite API v2 response spec
  field-by-field — all renamed to snake_case and present as real columns,
  so wiring up a real sync later is a field-mapping exercise, not a schema
  redesign. `applications.consent_status`/`personal_data_processing_status`/
  `has_artifacts` are real Jobvite GDPR/compliance fields, not demo filler.
- **`compensation_benchmarks`** — market pay-range data per position (min/
  mid/max, source, as-of date). No Jobvite/Dayforce API provides this —
  it's a reference table meant to be loaded by hand from an external
  compensation survey (Radford, Mercer, etc.) once you have one; the seed
  script leaves it empty rather than inventing benchmark numbers.

**Fields removed vs. the original charter-derived schema:**
`candidates.gender`/`race_ethnicity` and `employees.race_ethnicity` were
invented for fuller-looking demo data but were never backed by a real,
implemented API call in either this repo or `main`'s — removed rather than
carried forward as if they were real. `employees.gender` was kept: it's a
confirmed real field on Dayforce's base `Employees` resource (see
`dayforce_mapper.py`'s docstring), independently verified and already
mapped by `sync_employees`.

## RBAC

Five roles, enforced server-side on every data route (`src/core/deps.py`,
`src/api/routers/employees.py`, `recruiting.py`, `dashboard.py`):

- **Row-level:** `hr_business_partner` users are scoped to specific
  departments via `user_department_scopes`; every other role sees all
  departments.
- **Column/feature-level:** `can_view_compensation` (false for `recruiter`
  and `viewer`) hides salary/compa-ratio on employees and zeroes
  `salary_min`/`salary_max` on requisitions regardless of department scope
  — a recruiter never sees pay data even for their own department's
  requisitions.
- **Route-level:** `require_roles(...)` gates entire endpoints (e.g., only
  admins can manage users or trigger a sync).

Auth is local email/password + JWT (`src/utils/auth.py`,
`src/api/routers/auth.py`) — no Entra/SSO wiring in this build.

## API integrations: real code, placeholder credentials

`src/api/jobvite.py` / `src/api/dayforce.py` call these — they're **real,
implemented integrations**, not stubs: genuine HTTP calls, genuine auth
flows, checked against the actual public developer docs. They've never
succeeded end-to-end because no real credentials exist yet — calling
either today reaches the real Jobvite/Dayforce servers and comes back with
a real auth error (verified: Jobvite returns `401 Invalid api/secret`,
Dayforce's identity service returns `invalid_grant`), logged to
`ingestion_runs` either way.

- **`src/api/clients/jobvite_client.py`** — GET Job (requisitions), GET
  Candidate, GET Interview, GET Department, authenticated via Jobvite's
  `x-jvi-api`/`x-jvi-sc` header scheme — see the client's module docstring
  for an unresolved question about whether this or the doc's
  query-string/HMAC schemes is actually current; left unchanged pending a
  real credential to test against.
- **`src/api/clients/dayforce_client.py`** — the documented `POST
  /connect/token` password-grant flow (confirmed correct against Dayforce's
  official guide), then Bearer-token calls to `/Employees`,
  `/Employees/{XRefCode}/WorkAssignments`, `/CompensationSummary`,
  `/OrgUnitInfos`, `/Locations`.
- **`src/api/clients/*_mapper.py`** — raw API JSON → our column names.
  The Jobvite mapper is checked field-by-field against the API doc's
  response-spec tables, with two known param issues already fixed
  (`jobStatus` not `status`; `GET /department` is paginated). The Dayforce
  `WorkAssignments`/`CompensationSummary` mapper is flagged `UNVERIFIED` in
  its own docstring — informed by a third-party connector's documented
  schema, not a primary Dayforce source, so still needs confirming against
  a real tenant response.
- **`src/api/jobvite.py`** / **`src/api/dayforce.py`** — call the clients,
  run the mappers, best-effort upsert into the real tables (resolving
  department/location by name match), and log every attempt to
  `IngestionRun`.

**To actually go live:** fill in real values in `backend/.env` for whichever
system you have credentials for first — nothing else needs to change.

## Known simplifications (by design, given scope)

- Recruiting and HRIS fake data are generated independently and are
  *plausible*, not perfectly reconciled 1:1 (e.g., a "Hired" application's
  `hire_date` doesn't link to a specific row in `employees`). Acceptable for
  demoing the dashboards; a real integration would reconcile on an actual
  shared identifier.
- `export_powerbi.py` writes CSV, not Parquet — no extra Power BI
  connector/driver to install, trivial to open and sanity-check by hand,
  and the tables involved are a few thousand rows at most, so Parquet's
  size/type-fidelity advantages don't matter here.
- No automated tests. Given the fake-data/demo nature of this build, manual
  verification (seed → run server → exercise routes) was used instead; add
  tests before this becomes a real production system.
- SQLite is fine for this app's own read/write needs at a handful of
  concurrent users; a hosted DB (Postgres/Azure SQL) would be needed for
  meaningfully more concurrent load or for Power BI Service's scheduled
  *cloud* refresh (no native SQLite connector there).
- `GET /interview`'s documented required `eId` param is supported by the
  client but not yet supplied by `sync_interviews()` — we don't have a
  source for an interview-block id anywhere in our data yet; a real sync
  needs a discovery step first (see the client's docstring).
