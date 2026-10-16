from datetime import date
from typing import Optional
from schemas import AppBaseModel

class PerformanceReview(AppBaseModel):
    review_id: str
    employee_id: str
    review_period: str
    review_date: date
    rating: str
    reviewer_employee_id: str | None = None
    comments: str | None = None

class CalibrationReview(AppBaseModel):
    calibration_id: str
    employee_id: str
    review_id: str
    original_rating: str
    calibrated_rating: str
    calibration_date: date

class PromotionOutcome(AppBaseModel):
    promotion_outcome_id: str
    employee_id: str
    review_id: str
    promotion_date: date
    promoted: bool
    previous_position_id: str
    new_position_id: str

class PerformanceExit(AppBaseModel):
    performance_exit_id: str
    employee_id: str
    termination_date: date
    termination_reason: str
    performance_related: bool = False
