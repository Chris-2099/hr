from datetime import date
from typing import Optional
from api.schemas.common import AppBaseModel

class Employee(AppBaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[str] = None
    roles: Optional[str] = None
    start_date: Optional[date] = None
    employment_status: str
    employee_type: Optional[str] = None  # FT/PT/Contractor

class Department(AppBaseModel):
    jobvite_id: str | None = None
    dayforce_id: str | None = None
    department_id: str
    department_name: str

class Position(AppBaseModel):
    position_id: str
    title: str
    department_id: str
    manager_position_id: Optional[str] = None
    is_critical: bool = False
    is_leadership: bool = False
    status: str      # Filled, Vacant, Frozen
    created_date: date

class EmployeeMovement(AppBaseModel):
    movement_id: str
    employee_id: str
    movement_type: str  # Promotion, Transfer, Demotion, Lateral Move
    effective_date: date
    previous_position_id: str
    new_position_id: str
    previous_department_id: str
    new_department_id: str

class WorkforcePlan(AppBaseModel):
    workforce_plan_id: str
    department_id: str
    plan_month: date
    forecast_headcount: int
    budget_headcount: int
    actual_headcount: int
    expected_hires: int
    expected_exits: int
    required_headcount: int