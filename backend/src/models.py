from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


def _now() -> dt.datetime:
    return dt.datetime.utcnow()


# ---------------------------------------------------------------------------
# RBAC / Auth
# ---------------------------------------------------------------------------
# Role names drive both feature access (which dashboards/routes) and the two
# row/column-level restrictions the charter calls out as a key risk
# mitigation ("Row-level security and role-based access"):
#   - row-level: hr_business_partner is scoped to specific departments via
#     UserDepartmentScope; everyone else sees all departments.
#   - column-level: can_view_compensation gates salary/comp fields regardless
#     of department scope (recruiter and viewer never see pay data).
ROLE_ADMIN = "admin"
ROLE_EXECUTIVE = "executive"
ROLE_HRBP = "hr_business_partner"
ROLE_RECRUITER = "recruiter"
ROLE_VIEWER = "viewer"

ROLE_COMP_VISIBILITY = {
    ROLE_ADMIN: True,
    ROLE_EXECUTIVE: True,
    ROLE_HRBP: True,
    ROLE_RECRUITER: False,
    ROLE_VIEWER: False,
}


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    # Nullable because an Entra-SSO-only account never sets a local password.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), default="local")  # local | entra
    entra_object_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    employee_id: Mapped[str | None] = mapped_column(ForeignKey("employees.employee_id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)
    last_login_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped[Role] = relationship(back_populates="users")
    department_scopes: Mapped[list["UserDepartmentScope"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserDepartmentScope(Base):
    """Row-level access grant: which departments an HRBP user may see."""

    __tablename__ = "user_department_scopes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))

    user: Mapped[User] = relationship(back_populates="department_scopes")


# ---------------------------------------------------------------------------
# Org structure (Dayforce-sourced)
# ---------------------------------------------------------------------------
# Dayforce's REST API identifies every resource by a customer-assigned,
# stable `XRefCode` (see GET /Employees, /OrgUnitInfos?, /Locations, etc. in
# the RESTful Web Services Developer Guide) rather than an internal numeric
# id. `*_xref_code` columns below hold that value so a real sync can upsert
# on it directly; `*_id` stays our own internal primary key.
class Location(Base):
    __tablename__ = "locations"

    location_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    dayforce_xref_code: Mapped[str] = mapped_column(String(30), unique=True)  # Dayforce Locations.XRefCode
    name: Mapped[str] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100))
    remote_type: Mapped[str] = mapped_column(String(30), default="Onsite")  # Onsite|Hybrid|Remote


class Department(Base):
    """Dayforce models this as an Org Unit (`OrgUnitInfos`, `OrgUnitXRefCode`)."""

    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    dayforce_xref_code: Mapped[str] = mapped_column(String(30), unique=True)  # Dayforce OrgUnitXRefCode
    name: Mapped[str] = mapped_column(String(150))
    division: Mapped[str] = mapped_column(String(150))
    parent_department_id: Mapped[str | None] = mapped_column(
        ForeignKey("departments.department_id"), nullable=True
    )
    # No FK constraint here (would create departments<->employees cycle);
    # value still points at employees.employee_id by convention.
    leader_employee_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Position(Base):
    """Dayforce has no single "Position" resource; this stands in for the
    job-code-ish data carried on an employee's `WorkAssignments` entry
    (JobXRefCode / PositionXRefCode, job title, job level)."""

    __tablename__ = "positions"

    position_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    dayforce_xref_code: Mapped[str] = mapped_column(String(30), unique=True)  # WorkAssignment JobXRefCode
    title: Mapped[str] = mapped_column(String(150))
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))
    job_family: Mapped[str] = mapped_column(String(100))
    job_level: Mapped[int] = mapped_column(Integer)  # 1 (IC) .. 7 (exec)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    is_leadership: Mapped[bool] = mapped_column(Boolean, default=False)
    pay_grade: Mapped[str] = mapped_column(String(10), default="")
    status: Mapped[str] = mapped_column(String(20), default="Active")


class Employee(Base):
    """Maps to Dayforce's `/Employees/{XRefCode}` resource plus the
    org-placement fields that live on its `WorkAssignments` subordinate
    resource (department/position/location/manager). Dayforce keeps
    WorkAssignments effective-dated history; this table holds only the
    current assignment - same simplification as Compensation's "latest row
    wins" pattern, just without the history rows. A real sync would need a
    WorkAssignment-history table to reproduce point-in-time org charts
    exactly; out of scope for this build."""

    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    dayforce_employee_id: Mapped[str] = mapped_column(String(20), unique=True)  # Dayforce Employees.XRefCode
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    gender: Mapped[str] = mapped_column(String(30))
    race_ethnicity: Mapped[str] = mapped_column(String(50))  # Dayforce: Ethnicities subordinate resource
    birth_date: Mapped[dt.date] = mapped_column(Date)
    hire_date: Mapped[dt.date] = mapped_column(Date)
    termination_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    termination_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Voluntary|Involuntary
    termination_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    regrettable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # Dayforce: EmploymentStatusXRefCode (e.g. "Active"/"Terminated"/"Leave")
    employment_status: Mapped[str] = mapped_column(String(20), default="Active")
    employee_type: Mapped[str] = mapped_column(String(20), default="FTE")  # FTE|Part-Time|Contractor
    fte_percent: Mapped[float] = mapped_column(Float, default=1.0)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))
    position_id: Mapped[str] = mapped_column(ForeignKey("positions.position_id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.location_id"))
    manager_employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )
    remote_type: Mapped[str] = mapped_column(String(20), default="Onsite")
    is_high_potential: Mapped[bool] = mapped_column(Boolean, default=False)
    last_performance_rating: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_promotion_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)


class Compensation(Base):
    """One row per effective-dated comp change; current = latest per employee."""

    __tablename__ = "compensation"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    effective_date: Mapped[dt.date] = mapped_column(Date)
    base_salary: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    pay_frequency: Mapped[str] = mapped_column(String(20), default="Annually")
    bonus_target_pct: Mapped[float] = mapped_column(Float, default=0.0)
    equity_value: Mapped[float] = mapped_column(Float, default=0.0)
    compa_ratio: Mapped[float] = mapped_column(Float)  # salary / range midpoint
    change_reason: Mapped[str] = mapped_column(String(50), default="Annual Merit")


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    review_period: Mapped[str] = mapped_column(String(20))  # e.g. "2025-H2"
    rating: Mapped[str] = mapped_column(String(30))  # Low|Meets|Exceeds|High Performer
    rating_score: Mapped[int] = mapped_column(Integer)  # 1-5
    goal_completion_pct: Mapped[float] = mapped_column(Float)
    reviewer_employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )


class PtoUsage(Base):
    __tablename__ = "pto_usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    period: Mapped[str] = mapped_column(String(10))  # "2025-09"
    pto_hours_used: Mapped[float] = mapped_column(Float)
    pto_hours_available: Mapped[float] = mapped_column(Float)
    absenteeism_days: Mapped[float] = mapped_column(Float, default=0.0)


class EmployeeRelationsCase(Base):
    __tablename__ = "employee_relations_cases"

    case_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))
    case_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))  # Low|Medium|High
    opened_date: Mapped[dt.date] = mapped_column(Date)
    closed_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="ER Intake")  # ER Intake|Ethics Hotline


class EngagementSurvey(Base):
    __tablename__ = "engagement_surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    period: Mapped[str] = mapped_column(String(10))  # "2025-Q3"
    launched_date: Mapped[dt.date] = mapped_column(Date)
    closed_date: Mapped[dt.date] = mapped_column(Date)
    eligible_count: Mapped[int] = mapped_column(Integer)
    responded_count: Mapped[int] = mapped_column(Integer)


class EngagementResponse(Base):
    __tablename__ = "engagement_responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("engagement_surveys.id"))
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))
    # Anonymized by design (no employee_id) to mirror a real engagement tool.
    engagement_score: Mapped[float] = mapped_column(Float)  # 0-100
    leadership_confidence: Mapped[float] = mapped_column(Float)
    career_growth: Mapped[float] = mapped_column(Float)
    belonging: Mapped[float] = mapped_column(Float)
    recognition: Mapped[float] = mapped_column(Float)
    wellbeing: Mapped[float] = mapped_column(Float)
    manager_effectiveness: Mapped[float] = mapped_column(Float)
    sentiment: Mapped[str] = mapped_column(String(20), default="Neutral")  # Positive|Neutral|Negative


class SuccessionPlan(Base):
    __tablename__ = "succession_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    position_id: Mapped[str] = mapped_column(ForeignKey("positions.position_id"))
    successor_employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )
    readiness: Mapped[str] = mapped_column(String(20))  # Ready Now|Ready 1-2yr|Not Ready|No Successor


class TrainingCompletion(Base):
    __tablename__ = "training_completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    course_name: Mapped[str] = mapped_column(String(150))
    is_compliance: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="Not Started")  # Not Started|In Progress|Completed
    completion_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    hours: Mapped[float] = mapped_column(Float, default=0.0)


class WorkforcePlan(Base):
    __tablename__ = "workforce_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))
    plan_month: Mapped[dt.date] = mapped_column(Date)
    budget_headcount: Mapped[int] = mapped_column(Integer)
    forecast_headcount: Mapped[int] = mapped_column(Integer)
    actual_headcount: Mapped[int] = mapped_column(Integer)
    expected_hires: Mapped[int] = mapped_column(Integer)
    expected_exits: Mapped[int] = mapped_column(Integer)


# ---------------------------------------------------------------------------
# Recruiting (Jobvite-sourced)
# ---------------------------------------------------------------------------
# Column names below track the Jobvite API v2 "GET Requisition"/"GET
# Candidate"/"GET Interview" response field names 1:1 (snake_cased; `eId` ->
# `jobvite_eid`), per Jobvite-API-v2 04122025.pdf, so a real sync maps field
# -> column without a schema change.
class Requisition(Base):
    """Jobvite calls this the "job"/requisition resource."""

    __tablename__ = "requisitions"

    requisition_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    jobvite_eid: Mapped[str] = mapped_column(String(20), unique=True)  # job.eId
    title: Mapped[str] = mapped_column(String(150))
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"))  # job.department
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.location_id"))  # job.location / locationEId
    hiring_manager_employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    recruiter_employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))  # job.recruiters[]
    job_state: Mapped[str] = mapped_column(String(20))  # jobState: Open|Closed|Filled|On Hold|Draft (also Awaiting Approval|Approved|Rejected|Retracted)
    category: Mapped[str] = mapped_column(String(50))  # job.category
    eeo_category: Mapped[str] = mapped_column(String(50))  # job.eeoCategory
    posting_type: Mapped[str] = mapped_column(String(50), default="External")  # job.postingType
    remote_type: Mapped[str] = mapped_column(String(30), default="Onsite")  # job.remoteType
    position_count: Mapped[int] = mapped_column(Integer, default=1)  # job.positionCount
    salary_min: Mapped[float] = mapped_column(Float)  # job.salaryMin
    salary_max: Mapped[float] = mapped_column(Float)  # job.salaryMax
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")  # job.salaryCurrency
    salary_frequency: Mapped[str] = mapped_column(String(20), default="Annually")  # job.salaryFrequency
    opened_date: Mapped[dt.date] = mapped_column(Date)
    target_close_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    closed_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    filled_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)  # job.filledDate


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    jobvite_eid: Mapped[str] = mapped_column(String(20), unique=True)  # candidates.eId
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)  # candidates.postalCode
    country: Mapped[str] = mapped_column(String(100))
    current_title: Mapped[str | None] = mapped_column(String(150), nullable=True)  # candidates.title
    current_company_name: Mapped[str | None] = mapped_column(String(150), nullable=True)  # candidates.companyName
    work_status: Mapped[str] = mapped_column(String(30), default="US Citizen")  # candidates.workStatus
    veteran_status: Mapped[str] = mapped_column(String(50), default="Not a Veteran")  # application.veteranStatus
    source: Mapped[str] = mapped_column(String(100))  # application.source
    source_type: Mapped[str] = mapped_column(String(50))  # application.sourceType: Jobboard|Career Site|Referral|Agency
    gender: Mapped[str] = mapped_column(String(30))  # application.gender
    race_ethnicity: Mapped[str] = mapped_column(String(50))  # candidates.race
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)


class Application(Base):
    """Jobvite's per-requisition application record, nested under a
    candidate's response (`application.*` fields)."""

    __tablename__ = "applications"

    application_id: Mapped[str] = mapped_column(String(20), primary_key=True)  # application.eId
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.candidate_id"))
    requisition_id: Mapped[str] = mapped_column(ForeignKey("requisitions.requisition_id"))
    workflow_state: Mapped[str] = mapped_column(String(50))  # application.workflowState
    # Jobvite: workflowStateEId never changes even if the workflow state's
    # display name does - this is the field a real integration should key
    # pipeline-stage joins on, not workflow_state.
    workflow_state_eid: Mapped[str] = mapped_column(String(20))
    # New|Screening|Interview|Offer|Offer Accepted|Hired|Rejected|Withdrawn
    disposition: Mapped[str | None] = mapped_column(String(100), nullable=True)  # application.disposition
    applied_date: Mapped[dt.date] = mapped_column(Date)  # application.sentDate
    rejected_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    offer_extended_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    offer_accepted_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    hire_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)  # application.hireDate
    start_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)  # application.startDate
    hired_employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )
    offer_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_hire_90day_retained: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    new_hire_1yr_retained: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    hiring_manager_satisfaction: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5


class Interview(Base):
    __tablename__ = "interviews"

    interview_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    # Jobvite's interviewEId: the slot-level id for this specific
    # interviewer, distinct from the block-level eId on the parent response.
    jobvite_interview_eid: Mapped[str] = mapped_column(String(20), unique=True)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.application_id"))  # applicationEid
    interviewer_employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))  # interviewers[].userEId
    scheduled_date: Mapped[dt.date] = mapped_column(Date)  # interviews[].startTime
    duration_minutes: Mapped[int] = mapped_column(Integer)  # interviews[].duration
    timezone: Mapped[str] = mapped_column(String(50), default="America/Los_Angeles")  # interviewers[].timezone
    evaluation_link: Mapped[str] = mapped_column(String(255), default="")  # interviewers[].evaluationLink
    stage: Mapped[str] = mapped_column(String(50))  # Phone Screen|Panel|Final|Technical (not a raw Jobvite field - derived for reporting)
    status: Mapped[str] = mapped_column(String(20), default="Scheduled")  # interviewers[].status: Tentative|Accepted|Schedule
    # evaluation_score/recommendation summarize Jobvite's separate GET
    # Evaluation API (interview scorecards) rather than being raw Interview
    # fields - flattened here for a basic implementation.
    evaluation_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    recommendation: Mapped[str | None] = mapped_column(String(30), nullable=True)  # Strong Yes..Strong No


# ---------------------------------------------------------------------------
# Ingestion run log (stand-in for the "Monitor" pipeline stage)
# ---------------------------------------------------------------------------
class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_system: Mapped[str] = mapped_column(String(20))  # jobvite|dayforce|seed
    entity: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success")
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
