from datetime import date
from typing import Optional
from schemas import AppBaseModel

class LearningAssignment(AppBaseModel):
    assignment_id: str
    employee_id: str
    course_name: str
    assignment_type: str    # Required, Optional, Compliance, leadership
    assigned_date: date
    due_date: date | None = None
    completed: bool = False
    completion_date: date | None = None

class LearningEnrollment(AppBaseModel):
    enrollment_id: str
    employee_id: str
    program_name: str
    enrollment_date: date
    status: str             # Enrolled, Active, Completed, Withdrawn

class Certification(AppBaseModel):
    certification_id: str
    employee_id: str
    certification_name: str
    achieved_date: date
    expiration_date: date | None = None
    active: bool = True

class LearningOutcome(AppBaseModel):
    outcome_id: str
    employee_id: str
    learning_assignment_id: str
    outcome_type: str       # Promotion, Internal Mobility, Certification, Skill Growth
    outcome_date: date