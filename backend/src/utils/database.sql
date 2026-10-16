-- =====================================================
-- Departments
-- =====================================================
-- Columns reconciled 2026-10-16: department_id now holds a stable external
-- id (Jobvite eId for now; Dayforce's id once that source exists and the two
-- are reconciled), never the display name, since this key is joined against
-- by nearly every other table. See docs/backend-audit.md section 5.
create table departments (
    department_id text primary key,
    jobvite_id text,
    dayforce_id text,
    department_name text not null,
    parent_department_id text,
    leader_employee_id text,
    active boolean not null default true
);
-- =====================================================
-- Positions
-- =====================================================
create table positions (
    position_id text primary key,
    title text not null,
    department_id text not null,
    manager_position_id text,
    is_critical boolean not null default false,
    is_leadership boolean not null default false,
    status text not null,
    created_date timestamptz default now()
);
-- =====================================================
-- Employees
-- =====================================================
create table employees (
    employee_id text primary key,
    dayforce_id text,
    first_name text not null,
    last_name text not null,
    email text,
    department text,
    manager_id text,
    position_id text,
    hire_date date,
    termination_date date,
    employment_status text not null,
    employee_type text,
    created_at timestamptz default now()
);
-- =====================================================
-- Employee Movements
-- =====================================================
create table employee_movements (
    movement_id text primary key,
    employee_id text not null,
    movement_type text not null,
    effective_date date not null,
    previous_position_id text not null,
    new_position_id text not null,
    previous_department_id text not null,
    new_department_id text not null
);
-- =====================================================
-- Workforce Plans
-- =====================================================
create table workforce_plans (
    workforce_plan_id text primary key,
    department_id text not null,
    plan_month date not null,
    forecast_headcount integer not null,
    budget_headcount integer not null,
    actual_headcount integer not null,
    expected_hires integer not null,
    expected_exits integer not null,
    required_headcount integer not null
);
-- =====================================================
-- Foreign Keys
-- =====================================================
alter table positions
add constraint fk_positions_department
foreign key (department_id)
references departments(department_id);

alter table employees
add constraint fk_employees_position
foreign key (position_id)
references positions(position_id);

alter table employee_movements
add constraint fk_movements_employee
foreign key (employee_id)
references employees(employee_id);

alter table workforce_plans
add constraint fk_workforce_plans_department
foreign key (department_id)
references departments(department_id);
-- =====================================================
-- Candidates
-- =====================================================
create table candidates (
    candidate_id text primary key,
    first_name text not null,
    last_name text not null,
    email text,
    created_at timestamptz default now(),
    converted_employee_id text
);
-- =====================================================
-- Requisitions
-- =====================================================
-- Columns reconciled 2026-10-16 against the actual Jobvite /job payload and
-- api/schemas/recruiting.py:Requisition, which is what jobvite.py:sync_jobs
-- really maps. The original position_id/recruiter_id/status/job_open_date
-- columns assumed data Jobvite's /job endpoint never provides and were never
-- populated. See docs/backend-audit.md section 4/5.
create table requisitions (
    requisition_id text primary key,       -- Jobvite requisitionId
    jobvite_id text not null unique,       -- Jobvite eId
    title text not null,
    department_id text,                    -- nullable: Jobvite may omit department
    description text,                      -- plain-text, stripped of HTML on ingest
    recruiter_email text,
    hiring_manager_email text,
    job_state text not null,               -- Jobvite's own state (e.g. Active, Filled, Canceled)
    posting_type text,
    sent_date date not null,
    last_update_date date not null,
    created_at timestamptz default now()
);
-- =====================================================
-- Recruiting Sources
-- =====================================================
create table recruiting_sources (
    source_id text primary key,
    source_name text not null,
    source_type text not null
);
-- =====================================================
-- Applications
-- =====================================================
create table applications (
    application_id text primary key,
    candidate_id text not null,
    requisition_id text not null,
    source_id text,
    current_stage text not null,
    status text not null,
    applied_date date not null
);
-- =====================================================
-- Interviews
-- =====================================================
-- NOTE (2026-10-16): no confirmed Jobvite endpoint provides scheduled
-- interview events (date/time, status) as of this audit. Jobvite's public
-- surface appears to only expose interview *stages* as part of a workflow
-- (already captured via workflow_states.candidate_state_kind/isInterview),
-- not discrete scheduled-interview records. Verify against
-- developers.jobvite.com (requires tenant login) before building a sync for
-- this table - it may need to stay unpopulated, or be sourced from a
-- separate scheduling tool if one is in use. See docs/backend-audit.md.
create table interviews (
    interview_id text primary key,
    application_id text not null,
    interview_type text not null,
    scheduled_date timestamptz not null,
    status text not null
);
-- =====================================================
-- Offers
-- =====================================================
-- NOTE (2026-10-16): Jobvite exposes an Offer object, but third-party
-- integration guides (Knit) describe it as access granted per-customer on
-- request, separate from the job/candidate/application scopes this backend
-- currently has credentials for. Confirm with Jobvite/developers.jobvite.com
-- (requires tenant login) whether JOBVITE_API_KEY already has Offer access
-- and the exact endpoint/field names before building a sync for this table -
-- this is needed for time-to-fill, which currently has no other data source.
-- See docs/backend-audit.md.
create table offers (
    offer_id text primary key,
    application_id text not null,
    requisition_id text not null,
    offer_date date not null,
    status text not null,
    accepted_date date,
    declined_date date,
    proposed_start_date date
);
-- =====================================================
-- Recruiter Assignments
-- =====================================================
create table recruiter_assignments (
    assignment_id text primary key,
    recruiter_id text not null,
    requisition_id text not null,
    assigned_date date not null
);
-- =====================================================
-- Foreign Keys
-- =====================================================
alter table requisitions
add constraint fk_requisitions_department
foreign key (department_id)
references departments(department_id);

alter table candidates
add constraint fk_candidates_employee
foreign key (converted_employee_id)
references employees(employee_id);

alter table applications
add constraint fk_applications_candidate
foreign key (candidate_id)
references candidates(candidate_id);

alter table applications
add constraint fk_applications_requisition
foreign key (requisition_id)
references requisitions(requisition_id);

alter table applications
add constraint fk_applications_source
foreign key (source_id)
references recruiting_sources(source_id);

alter table interviews
add constraint fk_interviews_application
foreign key (application_id)
references applications(application_id);

alter table offers
add constraint fk_offers_application
foreign key (application_id)
references applications(application_id);
-- =====================================================
-- Performance Reviews
-- =====================================================

create table performance_reviews (
    review_id text primary key,

    employee_id text not null,

    review_period text not null,

    review_date date not null,

    rating text not null,

    reviewer_employee_id text,

    comments text
);

-- =====================================================
-- Calibration Reviews
-- =====================================================

create table calibration_reviews (
    calibration_id text primary key,

    employee_id text not null,

    review_id text not null,

    original_rating text not null,

    calibrated_rating text not null,

    calibration_date date not null
);

-- =====================================================
-- Promotion Outcomes
-- =====================================================

create table promotion_outcomes (
    promotion_outcome_id text primary key,

    employee_id text not null,

    review_id text not null,

    promotion_date date not null,

    promoted boolean not null,

    previous_position_id text not null,

    new_position_id text not null
);

-- =====================================================
-- Performance Exits
-- =====================================================

create table performance_exits (
    performance_exit_id text primary key,

    employee_id text not null,

    termination_date date not null,

    termination_reason text not null,

    performance_related boolean not null default false
);

-- =====================================================
-- Foreign Keys
-- =====================================================

alter table performance_reviews
add constraint fk_performance_reviews_employee
foreign key (employee_id)
references employees(employee_id);

alter table performance_reviews
add constraint fk_performance_reviews_reviewer
foreign key (reviewer_employee_id)
references employees(employee_id);

alter table calibration_reviews
add constraint fk_calibration_reviews_employee
foreign key (employee_id)
references employees(employee_id);

alter table calibration_reviews
add constraint fk_calibration_reviews_review
foreign key (review_id)
references performance_reviews(review_id);

alter table promotion_outcomes
add constraint fk_promotion_outcomes_employee
foreign key (employee_id)
references employees(employee_id);

alter table promotion_outcomes
add constraint fk_promotion_outcomes_review
foreign key (review_id)
references performance_reviews(review_id);

alter table promotion_outcomes
add constraint fk_promotion_outcomes_previous_position
foreign key (previous_position_id)
references positions(position_id);

alter table promotion_outcomes
add constraint fk_promotion_outcomes_new_position
foreign key (new_position_id)
references positions(position_id);

alter table performance_exits
add constraint fk_performance_exits_employee
foreign key (employee_id)
references employees(employee_id);
-- =====================================================
-- Talent Assessments
-- =====================================================

create table talent_assessments (
    assessment_id text primary key,

    employee_id text not null,

    assessment_date date not null,

    performance_rating text,
    potential_rating text,

    is_high_potential boolean not null default false,

    readiness_level text not null,

    assessment_notes text
);

-- =====================================================
-- Critical Roles
-- =====================================================

create table critical_roles (
    critical_role_id text primary key,

    position_id text not null,

    department_id text not null,

    criticality_level text not null,

    business_impact text,

    active boolean not null default true
);

-- =====================================================
-- Successor Assignments
-- =====================================================

create table successor_assignments (
    successor_assignment_id text primary key,

    position_id text not null,

    employee_id text not null,

    readiness_level text not null,

    primary_successor boolean not null default false,

    assignment_date date not null
);

-- =====================================================
-- Succession Plans
-- =====================================================

create table succession_plans (
    succession_plan_id text primary key,

    position_id text not null,

    department_id text not null,

    succession_status text not null,

    review_date date not null
);

-- =====================================================
-- Foreign Keys
-- =====================================================

alter table talent_assessments
add constraint fk_talent_assessments_employee
foreign key (employee_id)
references employees(employee_id);

alter table critical_roles
add constraint fk_critical_roles_position
foreign key (position_id)
references positions(position_id);

alter table critical_roles
add constraint fk_critical_roles_department
foreign key (department_id)
references departments(department_id);

alter table successor_assignments
add constraint fk_successor_assignments_position
foreign key (position_id)
references positions(position_id);

alter table successor_assignments
add constraint fk_successor_assignments_employee
foreign key (employee_id)
references employees(employee_id);

alter table succession_plans
add constraint fk_succession_plans_position
foreign key (position_id)
references positions(position_id);

alter table succession_plans
add constraint fk_succession_plans_department
foreign key (department_id)
references departments(department_id);
-- =====================================================
-- Learning Assignments
-- =====================================================

create table learning_assignments (
    assignment_id text primary key,

    employee_id text not null,

    course_name text not null,

    assignment_type text not null,

    assigned_date date not null,

    due_date date,

    completed boolean not null default false,

    completion_date date
);

-- =====================================================
-- Learning Enrollments
-- =====================================================

create table learning_enrollments (
    enrollment_id text primary key,

    employee_id text not null,

    program_name text not null,

    enrollment_date date not null,

    status text not null
);

-- =====================================================
-- Certifications
-- =====================================================

create table certifications (
    certification_id text primary key,

    employee_id text not null,

    certification_name text not null,

    achieved_date date not null,

    expiration_date date,

    active boolean not null default true
);

-- =====================================================
-- Learning Outcomes
-- =====================================================

create table learning_outcomes (
    outcome_id text primary key,

    employee_id text not null,

    learning_assignment_id text not null,

    outcome_type text not null,

    outcome_date date not null
);

-- =====================================================
-- Foreign Keys
-- =====================================================

alter table learning_assignments
add constraint fk_learning_assignments_employee
foreign key (employee_id)
references employees(employee_id);

alter table learning_enrollments
add constraint fk_learning_enrollments_employee
foreign key (employee_id)
references employees(employee_id);

alter table certifications
add constraint fk_certifications_employee
foreign key (employee_id)
references employees(employee_id);

alter table learning_outcomes
add constraint fk_learning_outcomes_employee
foreign key (employee_id)
references employees(employee_id);

alter table learning_outcomes
add constraint fk_learning_outcomes_assignment
foreign key (learning_assignment_id)
references learning_assignments(assignment_id);
-- =====================================================
-- Compensation Records
-- =====================================================

create table compensation_records (
    compensation_id text primary key,

    employee_id text not null,

    salary numeric(12,2) not null,

    pay_grade text,

    midpoint_salary numeric(12,2),

    effective_date date not null,

    annual_bonus_target numeric(12,2)
);

-- =====================================================
-- Bonus Awards
-- =====================================================

create table bonus_awards (
    bonus_id text primary key,

    employee_id text not null,

    bonus_amount numeric(12,2) not null,

    bonus_type text not null,

    award_date date not null
);

-- =====================================================
-- Merit Cycles
-- =====================================================

create table merit_cycles (
    merit_cycle_id text primary key,

    cycle_name text not null,

    cycle_year integer not null,

    total_budget_amount numeric(14,2) not null,

    budget_percentage numeric(5,2) not null,

    effective_date date not null
);

-- =====================================================
-- Market Benchmarks
-- =====================================================

create table market_benchmarks (
    benchmark_id text primary key,

    position_id text not null,

    market_minimum numeric(12,2) not null,

    market_midpoint numeric(12,2) not null,

    market_maximum numeric(12,2) not null,

    benchmark_date date not null
);

-- =====================================================
-- Foreign Keys
-- =====================================================

alter table compensation_records
add constraint fk_compensation_records_employee
foreign key (employee_id)
references employees(employee_id);

alter table bonus_awards
add constraint fk_bonus_awards_employee
foreign key (employee_id)
references employees(employee_id);

alter table market_benchmarks
add constraint fk_market_benchmarks_position
foreign key (position_id)
references positions(position_id);

-- =====================================================
-- Pipeline / Operational Tables (added 2026-10-16)
-- =====================================================
-- Kept in a separate schema so Power BI's semantic model (built against the
-- curated tables above) isn't cluttered with ingestion-run bookkeeping.
-- NOTE: Supabase only exposes the `public` schema to PostgREST by default.
-- To let the FastAPI service (using supabase-py's `.schema("pipeline")`)
-- read/write these tables, add `pipeline` under
-- Project Settings > API > Exposed schemas in the Supabase dashboard, and
-- grant usage: `grant usage on schema pipeline to service_role;`
-- `grant all on all tables in schema pipeline to service_role;`

create schema if not exists pipeline;

-- Untouched copy of every page/response fetched from a source, kept so a
-- transform bug can be diagnosed or replayed without re-calling the source
-- API. This is the "raw" half of the charter's "Store (raw + curated)" stage.
create table pipeline.raw_payloads (
    id bigserial primary key,
    source text not null,              -- 'jobvite' | 'dayforce'
    entity text not null,              -- 'job' | 'candidate' | 'department' | 'workflow' | ...
    payload jsonb not null,
    fetched_at timestamptz not null default now()
);

create index idx_raw_payloads_source_entity_fetched
on pipeline.raw_payloads (source, entity, fetched_at desc);

-- One row per sync call. This is the "Monitor" stage: lets you see at a
-- glance whether a refresh actually succeeded and whether row counts match
-- what the source reported (the charter's >=95% accuracy target needs this
-- to be checkable, not assumed).
create table pipeline.ingestion_runs (
    run_id bigserial primary key,
    source text not null,
    entity text not null,
    started_at timestamptz not null default now(),
    finished_at timestamptz,
    status text not null default 'running',  -- running | success | partial | failed
    reported_total integer,                  -- total the source API said it had
    rows_processed integer,                  -- rows actually mapped/upserted
    error text
);

create index idx_ingestion_runs_source_entity_started
on pipeline.ingestion_runs (source, entity, started_at desc);

-- =====================================================
-- Row-Level Security / EVP Access Mapping (added 2026-10-16)
-- =====================================================
-- Decision: database-level RLS (confirmed), not Power BI role-based security.
--
-- IMPORTANT DISTRIBUTION CAVEAT: this only filters per-EVP if each EVP's
-- report connects with a DISTINCT Postgres role that does not bypass RLS.
-- `service_role` (used by this FastAPI backend to ingest data) has BYPASSRLS
-- by default in Supabase, so it is unaffected by any of this - that's
-- intentional, ingestion must see everything. But a single shared Power BI
-- Service refresh identity used for ALL EVPs would ALSO see everything,
-- defeating the point. To actually get per-EVP filtering you need one of:
--   (a) a separate Postgres login role per EVP (e.g. evp_risk, evp_products),
--       each used by a SEPARATE Power BI dataset/connection scoped to that
--       EVP's App audience, with RLS policies keyed on current_user; or
--   (b) if Power BI ends up embedded in React, the embed-token-minting
--       endpoint opens its DB session as that viewer's specific role before
--       querying, rather than using one shared app-wide connection.
-- A single dataset + single shared DB login serving every EVP cannot be
-- filtered this way at the database level - that scenario needs Power BI's
-- own RLS roles instead (the option NOT chosen). Confirm which distribution
-- pattern applies before assuming this is fully solved. See
-- docs/backend-audit.md gap #3.

create table user_org_access (
    user_email text not null,       -- for app-level lookups (e.g. an embed-token endpoint)
    db_role text not null,          -- the Postgres role this EVP's Power BI connection logs in as
    evp_area text not null,         -- e.g. 'Risk', 'Products'
    department_id text not null references departments(department_id),
    primary key (db_role, department_id)
);

-- Reusable in every policy below instead of repeating the subquery.
create or replace function user_allowed_departments()
returns setof text
language sql
stable
security definer
as $$
    select department_id from user_org_access where db_role = current_user;
$$;

alter table departments enable row level security;
create policy evp_scoped_departments on departments
for select
using (department_id in (select user_allowed_departments()));

alter table requisitions enable row level security;
create policy evp_scoped_requisitions on requisitions
for select
using (department_id in (select user_allowed_departments()));

-- TEMPLATE for tables scoped indirectly (e.g. applications -> requisitions,
-- or any future Dayforce-sourced table keyed by employee_id ->
-- employees.department_id). Not yet applied broadly: most of the remaining
-- 20+ curated tables aren't populated yet (no Dayforce feed, unconfirmed
-- Jobvite offer/interview access - see gaps in docs/backend-audit.md), and
-- the live DB schema for them has already diverged from this file per the
-- stakeholder. Apply this pattern table-by-table as each one goes live:
--
-- alter table applications enable row level security;
-- create policy evp_scoped_applications on applications
-- for select
-- using (
--     requisition_id in (
--         select requisition_id from requisitions
--         where department_id in (select user_allowed_departments())
--     )
-- );