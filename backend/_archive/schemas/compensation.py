from datetime import date
from typing import Optional
from schemas import AppBaseModel

class CompensationRecord(AppBaseModel):
    compensation_id: str
    employee_id: str
    salary: float
    pay_grade: str | None = None
    midpoint_salary: float | None = None
    effective_date: date
    annual_bonus_target: float | None = None

class BonusAward(AppBaseModel):
    bonus_id: str
    employee_id: str
    bonus_amount: float
    bonus_type: str         # Annual, Spot, Retention, Sign-On
    award_date: date

class MeritCycle(AppBaseModel):
    merit_cycle_id: str
    cycle_name: str
    cycle_year: int
    total_budget_amount: float
    budget_percentage: float
    effective_date: date

class MarketBenchmark(AppBaseModel):
    benchmark_id: str
    position_id: str
    market_minimum: float
    market_midpoint: float
    market_maximum: float
    benchmark_date: date