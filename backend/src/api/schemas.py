from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    can_view_compensation: bool
    department_scope: list[str] | None  # None = all departments


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    department_scope: list[str]


class CreateUserRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str
    department_ids: list[str] = []


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: str
    name: str
    division: str
    jobvite_id: str | None
    active: bool


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    first_name: str
    last_name: str
    email: str
    department_id: str
    position_id: str
    location_id: str
    employment_status: str
    employee_type: str
    hire_date: dt.date
    termination_date: dt.date | None
    manager_employee_id: str | None
    gender: str
    remote_type: str
    last_performance_rating: str | None
    is_high_potential: bool
    base_salary: float | None = None
    compa_ratio: float | None = None


class RequisitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    requisition_id: str
    title: str
    department_id: str
    location_id: str
    job_state: str
    category: str
    position_count: int
    salary_min: float
    salary_max: float
    opened_date: dt.date
    target_close_date: dt.date | None
    closed_date: dt.date | None
    filled_date: dt.date | None


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    candidate_id: str
    first_name: str
    last_name: str
    email: str
    source: str
    source_type: str
    is_internal: bool


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    candidate_id: str
    requisition_id: str
    workflow_state: str
    disposition: str | None
    applied_date: dt.date
    hire_date: dt.date | None
    start_date: dt.date | None
    consent_status: str | None
    personal_data_processing_status: str | None
    has_artifacts: bool | None
