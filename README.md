# HR Workforce & Org Health Dashboard — Data Pipeline

A data pipeline for the dashboard described in the `HR_Workforce_OrgHealth
Dashboard Charter`. **The frontend is Power BI itself** — this repo no
longer serves a web app. The backend's only job is: pull from Jobvite (ATS)
+ Dayforce (HRIS), land it in a local database, and export that database to
a format Power BI can open.

The dashboards still run on fake data shaped like a real Jobvite/Dayforce
feed. **Real, working Jobvite/Dayforce API client code exists** (see "API
integrations" below) and makes genuine calls to those real services — it
just has no real credentials yet, so every call fails cleanly and logs the
attempt rather than silently doing nothing.

> This branch's `backend/src/` layout (`api/clients/`, `core/`, `utils/`)
> mirrors the structure of this repo's `main` branch, which is an earlier,
> Supabase/FastAPI-backed attempt at the same charter. This branch keeps
> that same shape so the two are easy to compare/copy between, but makes
> two deliberate different calls: SQLite instead of Supabase (self-contained,
> nothing to provision), and no FastAPI/server layer at all (see "Access
> control" below for why the RBAC layer went with it too).

## What's here

- **`backend/src/seed/seed_data.py`** — generates ~300 employees, ~2,000+
  recruiting/performance/engagement/compensation records into
  `backend/hr_dashboard.db` (SQLite). Fixed random seed — re-running it
  reproduces the same dataset byte-for-byte.
- **`backend/src/api/jobvite.py`** / **`backend/src/api/dayforce.py`** — the
  real ingestion pipeline, one module per source system: each calls its
  client (`src/api/clients/*_client.py`), maps the response onto our schema
  (`src/api/clients/*_mapper.py`), and upserts into the database. Logs
  every attempt (success or failure) to the `ingestion_runs` table.
- **`backend/src/export_powerbi.py`** — reads every table out of the
  database into a pandas DataFrame and writes one CSV per table. Point
  Power BI's "Get Data > Folder" (or "Text/CSV" per file) at the output
  directory.

There is no server process, no API, and no frontend code in this repo
anymore — just scripts you run (locally, via cron, via a scheduled
container, etc.) and a database they read/write.

## Quick start (local)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                        # defaults work as-is for local dev

python -m src.seed.seed_data                 # (re)creates hr_dashboard.db with fresh fake data
python -m src.api.jobvite                    # pulls from Jobvite, upserts into hr_dashboard.db
python -m src.api.dayforce                   # pulls from Dayforce, upserts into hr_dashboard.db
python -m src.export_powerbi                 # writes ./powerbi_export/*.csv

# In Power BI Desktop: Get Data > Folder > point at backend/powerbi_export/
```

Re-run `src.api.jobvite` / `src.api.dayforce` then `src.export_powerbi` (in
that order) any time you want Power BI's next refresh to pick up new data.

## Docker

```bash
docker compose run --rm backend
```

This is a one-shot pipeline run, not a long-lived service: seeds the DB on
first run only, runs each source's sync, then exports CSVs to
`./powerbi_export/` on the host (mounted volume). Run it on whatever
schedule you need — cron, Task Scheduler, a scheduled CI job, etc. There's
no port to expose and nothing to reverse-proxy; back up the SQLite file (or
the `hr_db` volume) on whatever schedule the org already uses for small
internal tools.

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
  `interviews`. Field names and types follow the Jobvite API v2 response
  spec field-by-field — all renamed to snake_case and present as real
  columns, so wiring up a real sync later is a field-mapping exercise, not a
  schema redesign.

`roles`, `users`, and `user_department_scopes` still exist as seeded data
(see "Access control" below) but nothing in this repo reads them to gate
access anymore.

## Access control: now Power BI's job, not this repo's

The previous version of this build enforced row/column-level security
(department scoping, compensation visibility) in a FastAPI RBAC layer,
because the frontend was a React app talking to our own API. Now that
Power BI is the frontend, **Power BI's native Row-Level Security** is the
right place for that: define roles in the `.pbix` model and map Entra ID
users/groups to them in the Power BI Service, rather than reimplementing
department/compensation scoping here for an API nothing calls anymore.

The `users` / `roles` / `user_department_scopes` tables (with bcrypt
password hashes from `src.utils.auth.hash_password`) are still seeded,
since they may be useful as an RLS mapping table (e.g. a DAX filter
comparing `USERPRINCIPALNAME()` against `users.email` + department scope)
once the Power BI model is built — but that's a data-modeling decision to
make inside Power BI, not code to write here.

## API integrations: real code, placeholder credentials

`src/api/jobvite.py` / `src/api/dayforce.py` call these — they're **real,
implemented integrations**, not stubs: genuine HTTP calls, genuine auth
flows, confirmed against the actual public developer docs during this
build. They've never succeeded end-to-end because no real credentials
exist yet — calling either today reaches the real Jobvite/Dayforce servers
and comes back with a real auth error (verified: Jobvite returns `401
Invalid api/secret`, Dayforce's identity service returns `invalid_grant`),
logged to `ingestion_runs` either way.

- **`src/api/clients/jobvite_client.py`** — GET Job (requisitions), GET
  Candidate, GET Interview, authenticated via Jobvite's documented
  `x-jvi-api`/`x-jvi-sc` header scheme.
- **`src/api/clients/dayforce_client.py`** — the documented `POST
  /connect/token` password-grant flow, then Bearer-token calls to
  `/Employees`, `/Employees/{XRefCode}/WorkAssignments`,
  `/CompensationSummary`, `/OrgUnitInfos`, `/Locations`.
- **`src/api/clients/*_mapper.py`** — raw API JSON → our column names.
  The Jobvite mapper is verified field-by-field against the API doc's
  response-spec tables. The Dayforce `WorkAssignments`/`CompensationSummary`
  mapper is flagged `UNVERIFIED` in its own docstring — Dayforce's doc page
  names those as subordinate endpoints without listing their field shapes,
  so those specific field names are an informed guess, not a confirmed fact.
- **`src/api/jobvite.py`** / **`src/api/dayforce.py`** — call the clients,
  run the mappers, best-effort upsert into the real tables (resolving
  department/location by name match), and log every attempt to
  `IngestionRun`.

**To actually go live:** fill in real values in `backend/.env` for whichever
system you have credentials for first — nothing else needs to change.

Dropped along with the frontend: the Power BI Embedded ("embed for your
organization") client and its MSAL.js/React embedding code. That pattern
existed only to embed a Power BI report *inside our own app's UI* — with no
app UI left, users open Power BI directly (Service, Desktop, or mobile) and
none of that embedding plumbing is needed.

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
  verification (seed → sync → export → open in Power BI) was used instead;
  add tests before this becomes a real production pipeline.
- SQLite is fine for this pipeline's own read/write needs, but Power BI
  Service has no native SQLite connector for *scheduled cloud refresh* —
  that needs a gateway-supported source (e.g. Postgres via an on-prem
  gateway, or Azure SQL Database) once this moves past manual/local
  refresh in Power BI Desktop.
- No in-process scheduler (the `main` branch's FastAPI build had one via
  APScheduler, running inside the server's lifespan). With no server to
  host it, "automated refresh" means an external scheduler (cron, Task
  Scheduler, a scheduled CI job) invoking `src.api.jobvite` /
  `src.api.dayforce` / `src.export_powerbi` directly — simpler than the
  in-process version since there's no HTTP hop to make either.
