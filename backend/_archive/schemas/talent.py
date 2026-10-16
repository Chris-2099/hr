from datetime import date
from typing import Optional
from schemas import AppBaseModel

class TalentAssessment(AppBaseModel):
    assessment_id: str
    employee_id: str
    assessment_date: date
    performance_rating: Optional[str] = None
    potential_rating: Optional[str] = None
    is_high_potential: bool = False
    readiness_level: str        # Ready Now, Ready <1 Year, Ready 1-2 Years,  Not Ready
    assessment_notes: Optional[str] = None

class CriticalRole(AppBaseModel):
    critical_role_id: str
    position_id: str
    department_id: str
    criticality_level: str      # High ,Medium, Low
    business_impact: Optional[str] = None
    active: bool = True

class SuccessorAssignment(AppBaseModel):
    successor_assignment_id: str
    position_id: str
    employee_id: str
    readiness_level: str        # Ready Now, <1 Year, 1-2 Years
    primary_successor: bool = False
    assignment_date: date

class SuccessionPlan(AppBaseModel):
    succession_plan_id: str
    position_id: str
    department_id: str
    succession_status: str      # covered, at risk, uncovered
    review_date: date