# Backend Audit — HR Executive Workforce Intelligence

Audit only. No code was changed, deleted, or refactored. Scope: `backend/` (the
`frontend/` directory is a separate app and is out of scope except where noted
as a dependency to remove).

Charter reference used for this audit (pasted by user into chat, not a repo
file): Power BI App delivery, Dayforce + Jobvite only, RLS per EVP, >=95%
accuracy, one metric dictionary, 12-week timeline, pipeline =
Extract → Transform → Validate → Store (raw+curated) → Semantic model →
Secure (RLS) → Refresh → Monitor.

---

## 1. Inventory

Repo is small: **1,670 lines across 18 files**, all Python (FastAPI).

| Path | Purpose |
|---|---|
| `src/main.py` | FastAPI app factory, lifespan hook that pings Supabase on boot, `/` and `/health` endpoints, mounts 3 routers. |
| `src/core/config.py` | `pydantic-settings` config: Supabase, Jobvite, and Dayforce (optional) env vars. |
| `src/core/supabase_client.py` | Instantiates a single Supabase client using the **secret** (service-role) key. |
| `src/api/clients/jobvite_client.py` | Thin `httpx` wrapper for 4 Jobvite REST endpoints: job, candidate, workflow, department. |
| `src/api/clients/dayforce_client.py` | **Empty file.** No Dayforce client exists. |
| `src/api/routers/jobvite.py` | Calls Jobvite client, maps raw JSON → Pydantic schemas, upserts into Supabase. 4 sync endpoints: job, candidate (+application), department, workflow. |
| `src/api/routers/dayforce.py` | **Stub.** Only a `/health` route, no ingestion logic. |
| `src/api/routers/database.py` | Read-only passthrough GET endpoints (`/jobs`, `/candidates`, `/applications`, `/departments`, `/workflows`) that `SELECT *` from Supabase and return JSON. |
| `src/api/schemas/*.py` | Pydantic models: `workforce.py` (Employee, Department, Position, EmployeeMovement, WorkforcePlan), `recruiting.py` (Candidate, Application, Requisition, WorkflowState) — both used. `talent.py`, `performance.py`, `learning.py`, `compensation.py` — **not used anywhere, and broken** (see §3). |
| `src/utils/database.py` | Generic `SupabaseDatabaseHelper` CRUD wrapper (insert/upsert/select/update/delete/count) used by routers. |
| `src/utils/database.sql` | Hand-written curated schema: 28 tables covering workforce, recruiting, performance, succession/talent, learning, compensation. No views, functions, or RLS policies. |
| `src/utils/utils.py` | `html_to_text` (strips Jobvite's HTML job descriptions), `timestamp_to_date` (epoch-ms → date), `get_table_records` (wraps a Supabase select in an HTTPException-safe response). |
| `requirements.txt` | Lists only `fastapi[standard]` and `supabase`. Does not list `pydantic-settings`, `beautifulsoup4`/`bs4`, or `httpx`, all of which are imported directly. |
| `Dockerfile` | Standard slim-Python image, non-root user, runs uvicorn. |
| `.env` | Supabase URL/publishable key/secret key/JWKS URL; Jobvite URL/key/secret. No Dayforce values present yet. |

**Could not verify:** actual Dayforce API shape/auth model (no client code,
no sample payloads in repo), whether Supabase is meant to be permanent
storage or a staging step toward another target, and whether any of this is
already deployed/scheduled anywhere (no CI, cron, or scheduler config found
in the repo).

---

## 2. Stage Mapping

| Pipeline Stage | Status | Evidence |
|---|---|---|
| **Extract** | **Partial** | Jobvite: real, working client (`jobvite_client.py`) for job/candidate/workflow/department. Dayforce: **Missing** — `dayforce_client.py` is empty, `dayforce.py` router has no ingestion route. |
| **Transform** | **Partial** | Jobvite → Pydantic mapping exists in `jobvite.py` (field renames, HTML stripping, epoch→date). No transform logic exists for Dayforce (nothing to transform). No transform/derivation logic for *any* computed metric (attrition rate, tenure, time-to-fill) — only raw field mapping. |
| **Validate** | **Mock/Hardcoded** | Only validation is Pydantic type coercion at ingestion (e.g., required fields will raise if missing). No accuracy/reconciliation checks, no row-count or null-rate thresholds, nothing enforcing the charter's >=95% accuracy target. |
| **Store (raw + curated)** | **Partial** | A single curated Postgres schema exists (`database.sql`, Supabase-hosted) — no separate raw/landing layer. Upserts write directly into curated tables (`on_conflict=...`), so there's no raw snapshot to replay/audit from if a transform bug is found later. |
| **Semantic model** | **Missing** | No Power BI `.pbix`, dataset, or DAX measure files in this repo. No metric calculation logic anywhere in the backend (see §4) — nothing for Power BI to build a semantic layer on top of beyond raw table columns. |
| **Secure (RLS)** | **Missing** | No RLS policies in `database.sql`. No user-to-EVP/org mapping table exists. No auth/JWT middleware in the FastAPI app despite a `SUPABASE_JWKS_URL` being defined in `.env` (suggests auth was planned but never wired up). |
| **Refresh** | **Missing** | All sync endpoints (`/api/jobvite/*/sync`) are manually triggered HTTP POSTs. No scheduler, cron, Celery/task-queue, or webhook listener in the repo to automate refresh. |
| **Monitor** | **Missing** | No logging framework (just `print()` in `main.py`), no error-rate tracking, no alerting, no ingestion-run audit table (last-synced timestamp, row counts, failures). |

**Bottom line:** of the 8 stages, only two have real, working code (Extract and Transform, and only for Jobvite). Six stages are partial, mocked, or fully missing.

---

## 3. Keep / Remove / Rewrite

### Keep
- `src/api/clients/jobvite_client.py` — clean, minimal, correctly handles Jobvite's auth headers.
- `src/api/routers/jobvite.py` ingestion logic (sync endpoints) — real mapping logic, upsert-based (idempotent), decent error translation from `httpx` exceptions to `HTTPException`. This is the one genuinely load-bearing piece of the backend.
- `src/utils/database.py` (`SupabaseDatabaseHelper`) — generic, reusable, no dead weight.
- `src/utils/utils.py` helpers (`html_to_text`, `timestamp_to_date`) — small, correct, specific to real Jobvite payload quirks.
- `src/utils/database.sql` — a genuinely useful curated schema covering every metric theme in the charter (workforce, recruiting, performance, succession, learning, compensation). This is the best asset in the repo and should anchor the "Store" stage design, even though most of its 28 tables have no ingestion path yet.
- `src/api/schemas/workforce.py`, `recruiting.py`, `common.py` — correctly used, matches the SQL schema reasonably well.

### Remove (once Power BI replaces this role)
- **`src/api/routers/database.py`** — these GET endpoints exist only to serve JSON to a UI client (the React frontend). Power BI connects to Postgres/Supabase directly via its native connector; it does not need a REST passthrough layer. This is the clearest "built for the old architecture" artifact in the repo.
- **`SUPABASE_PUBLISHABLE_KEY`** in `.env`/`config.py` — the publishable (anon/browser) key is only meaningful for a client-side app enforcing RLS per logged-in user. If Power BI authenticates to Postgres directly (service account or RLS-aware DB role) and the React app is fully retired, this key has no remaining consumer. **Pending:** a Power BI-embedded-in-React path is under consideration (access request in progress). If that path is approved, React keeps a reason to exist as the embed host and likely keeps its own auth (Supabase Auth, given `SUPABASE_JWKS_URL` is already present) — in which case this key stays, repurposed for "who's allowed to request an embedded report for which EVP" rather than for serving raw data. Don't remove this until the embed-access decision lands.
- **`src/api/schemas/talent.py`, `performance.py`, `learning.py`, `compensation.py`** — **dead code, and currently broken.** All four import `from schemas import AppBaseModel`, but the actual module is `api.schemas.common`. There is no top-level `schemas` package, so importing any of these four files raises `ModuleNotFoundError` today. Nothing in the app imports them, so the bug is latent — but they're not "working code to keep," they're unfinished scaffolding.

### Rewrite / Needs real work (not currently code worth preserving as-is)
- **Dayforce integration** — effectively needs to be built from scratch (empty client, stub router). This is a bigger gap than Jobvite's and blocks most workforce-snapshot and retention metrics.
- **`requirements.txt`** — doesn't match actual imports (`pydantic-settings`, `bs4`/`beautifulsoup4`, `httpx` are used but not pinned). Will break a clean install.
- **Validation stage** — doesn't exist beyond Pydantic type checks; needs a real design (row counts vs. source, null-rate checks, referential integrity against the FK structure already defined in SQL).
- **Refresh/scheduling** — nothing to "rewrite," but a scheduling mechanism (cron, Azure Data Factory, GitHub Actions, Supabase scheduled functions, etc.) needs to be chosen and added.

---

## 4. Draft Metric Dictionary

**No metric calculation logic exists anywhere in this codebase.** The
ingestion code only maps and stores raw source fields; it does not compute
rates, ratios, or aggregates. The table below reflects what the *stored
schema* would support if populated, not logic that currently runs. This is
the one correction worth noting up front since the task asked to "extract
each metric's current definition" — there isn't one to extract; there are
only the raw fields a future definition would be built from.

| Metric | Candidate formula | Source fields (current schema) | Grain | Known issues |
|---|---|---|---|---|
| Headcount | `COUNT(employees)` where `employment_status = 'Active'` | `employees.employment_status` | Point-in-time, by department/date | `employees` table has no ingestion path yet (no Dayforce sync); "Active" is a free-text status with no enforced enum. |
| Attrition rate | `COUNT(terminations in period) / AVG(headcount in period)` | `employees.termination_date`, `employees.employment_status` | Monthly/period, by department | Same — table is empty today. No distinction in schema between voluntary/involuntary termination (needed for "flight risk" theme) or termination reason. |
| Tenure | `termination_date or today - hire_date` | `employees.hire_date`, `employees.termination_date` | Per employee | Fine once populated; no issues beyond the missing Dayforce feed. |
| Time to fill | `offer.accepted_date - requisition.job_open_date` (or `offers.offer_date` if accepted) | `requisitions.job_open_date`, `offers.accepted_date` | Per requisition | `offers` table exists in SQL but has **no sync endpoint at all** — Jobvite ingestion only covers job/candidate/department/workflow, not offers or interviews. |
| Requisition aging | `today - requisitions.job_open_date` where `status = 'Open'` | `requisitions.job_open_date`, `requisitions.status` | Per open requisition | `requisitions` *is* populated via `/api/jobvite/job/sync`, but the mapped `Requisition` schema uses `job_state`/`last_update_date`/`sent_date`, which don't line up 1:1 with the SQL table's `status`/`job_open_date`/`job_close_date` columns — **the Pydantic schema and the SQL table have drifted from each other** and need reconciling before this is usable. |
| Promotion rate | `COUNT(promotion_outcomes where promoted=true) / headcount` | `promotion_outcomes.promoted` | Period, by department | Table exists in SQL; no ingestion source identified yet (not in Dayforce/Jobvite scope as currently understood — needs clarification, see §5). |
| Performance rating distribution | `COUNT(performance_reviews) GROUP BY rating` | `performance_reviews.rating` | Per review cycle | Table exists in SQL; no ingestion path. Source system for performance reviews not confirmed as Dayforce. |
| Compensation ratio (compa-ratio) | `salary / midpoint_salary` | `compensation_records.salary`, `.midpoint_salary` | Per employee | Table exists in SQL; no ingestion path; sensitive data — needs its own RLS/access consideration beyond generic EVP scoping. |

**I could not verify** which of performance, learning, succession, and
compensation data actually lives in Dayforce vs. a separate system — the
charter pasted in chat says "Dayforce and Jobvite only," but Dayforce is
usually HRIS-core (employee master, comp, sometimes performance) while
things like succession planning or LMS data are often separate modules or
tools. Recommend confirming with the Dayforce admin which modules are
licensed/accessible before building against the compensation/performance/
succession/learning tables.

---

## 5. Charter Gaps

1. **Dayforce has zero ingestion code.** Employee master data (headcount,
   tenure, department, manager, termination) is the foundation most other
   metrics join against (e.g., attrition needs headcount as denominator).
   This is the single largest gap against the 12-week timeline.
2. **Data not obtainable from Dayforce/Jobvite alone:** revenue-per-employee
   and labor-cost-% of revenue (mentioned as a general risk for this kind of
   dashboard) would need a finance data source — out of charter scope as
   written, but worth flagging now if leadership expects to see those on the
   scorecard later. **Needs a decision from you**, not an assumption.
3. **RLS / user-to-EVP mapping — now implemented, decision made: database-
   level RLS.** `user_org_access` table + a `user_allowed_departments()`
   helper + example policies on `departments`/`requisitions` were added to
   `database.sql` 2026-10-16. **Remaining open issue (distribution model):**
   this only filters per-EVP if each EVP's Power BI connection logs in as a
   *distinct* Postgres role — `service_role` (used for ingestion) bypasses
   RLS entirely by design, and a *single shared* Power BI Service refresh
   identity used for every EVP would also see everything, defeating the
   point. Getting real per-EVP filtering needs either (a) one Postgres role
   + one Power BI dataset per EVP App audience, or (b) if Power BI ends up
   embedded in React, the embed-token-minting endpoint opening its DB
   session as that specific viewer's role rather than one shared app-wide
   connection. A single dataset shared by all EVPs through one DB login
   cannot be filtered this way — that scenario needs Power BI's own RLS
   roles instead, which is the option that was explicitly not chosen. This
   needs a decision on distribution model before it's actually solved, not
   just implemented in SQL.
4. **Validation/reconciliation is undesigned.** Nothing checks that a sync
   actually captured all records (e.g., comparing Jobvite's reported
   `total` to the count actually upserted — the code reads `total` from the
   response but never compares it to `len(jobs)` actually processed).
5. **No raw/landing layer.** Everything upserts straight into curated
   tables. If a transform bug is found after the fact, there's no raw
   snapshot to reprocess from — only whatever is already overwritten in the
   curated table.
6. **Schema/Pydantic drift.** The recruiting schema (`Requisition`) and the
   SQL table (`requisitions`) already disagree on field names (see §4,
   time-to-fill row). This will get worse as more entities are wired up
   unless reconciled now.
7. **No scheduling/orchestration mechanism chosen.** Needed for "automated
   refresh" success criterion — currently 100% manual (`POST .../sync`).
8. **No monitoring/alerting.** Needed to catch the ">=95% accuracy" and
   data-quality risks called out in the charter before they reach
   executives.
9. **Offers and interviews may not be obtainable from Jobvite's granted API
   scope.** Jobvite exposes an Offer object, but third-party integration
   docs describe access to it as granted per-customer on request, separate
   from the job/candidate/application scopes already in use here — it's
   unconfirmed whether the current `JOBVITE_API_KEY` includes it. Scheduled
   interview events (date/time, status) don't appear to be exposed by
   Jobvite's core API at all — only interview *stages* as part of a workflow
   (already captured via `workflow_states`). Time-to-fill (needs offers) and
   any interview-funnel metric are blocked on this until confirmed via
   developers.jobvite.com (requires your tenant login) or Jobvite support.

---

## 6. Recommended Plan (12 weeks)

**Storage recommendation: keep Supabase (Postgres) as curated store, add a raw/staging schema inside the same Postgres instance — don't introduce Fabric/Azure SQL yet.**

Reasoning: the charter's scope is two sources, moderate volume (HR +
recruiting data, not high-frequency transactional data), and a 12-week
timeline. Supabase/Postgres already has real work invested in it (the
28-table curated schema) and Power BI's native Postgres connector supports
scheduled refresh and DirectQuery/Import modes without extra integration
work. Introducing Fabric Lakehouse or Azure SQL now would mean re-doing
schema and connection work that's already done, for benefits (lakehouse-
scale compute, OneLake integration) that aren't needed at this data volume.
Revisit this only if: (a) data volume or source count grows significantly
later, or (b) your org standardizes on Fabric for governance/licensing
reasons outside this project's control.

**Suggested phasing (debloat first, then build):**

- **Weeks 1–2 (Debloat + reconcile):** Remove `database.py` router and the
  4 broken/unused schema files. Fix `requirements.txt`. Reconcile the
  `Requisition` Pydantic schema against the `requisitions` SQL table (and
  do the same check for every entity before building more). Confirm with
  stakeholders which source system actually owns performance/learning/
  succession/compensation data.
- **Weeks 2–4 (Dayforce extract):** Build `dayforce_client.py` and a real
  `dayforce.py` router following the same pattern as `jobvite.py` — this is
  the critical-path item since most metrics depend on employee master data.
- **Weeks 3–5 (Raw + validate):** Add a raw/staging schema (same Postgres
  instance, separate schema namespace) that sync jobs write to first; add a
  lightweight validation step (row-count match against source `total`,
  required-field null checks) before promoting raw → curated.
- **Weeks 4–6 (Remaining Jobvite entities):** Add `offers` and `interviews`
  sync (needed for time-to-fill and interview-funnel metrics), which are
  currently missing despite having SQL tables.
- **Weeks 5–7 (Security):** Design and implement the user-to-EVP mapping
  table and RLS policies (or Power BI role-based security, per your
  decision in gap #3).
- **Weeks 6–8 (Semantic model):** Build the actual metric dictionary with
  signed-off formulas (this audit's §4 is a starting draft only) and the
  Power BI semantic model/measures on top of the curated schema.
- **Weeks 7–9 (Refresh + monitor):** Add scheduled refresh (Supabase
  scheduled functions, GitHub Actions cron, or similar) and a minimal
  monitoring/audit table (last sync time, rows processed, failures).
- **Weeks 9–12 (Dashboard build, UAT, deployment):** Power BI report build,
  RLS testing per EVP, stakeholder UAT, go-live.

This plan assumes the decisions flagged in §5 (finance data scope, RLS
approach, source-of-truth per module) get resolved early — they block
downstream work if left open.
