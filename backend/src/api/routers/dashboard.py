"""Cross-cutting summary metrics spanning both source systems - necessarily
combined, not source-specific like employees.py/recruiting.py."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src import models
from src.core.database import get_db
from src.core.deps import CurrentUser, department_filter_ids, get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    active_headcount: int
    open_requisitions: int
    total_candidates: int
    hires_to_date: int


@router.get("/summary", response_model=DashboardSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    all_ids = [d.department_id for d in db.query(models.Department.department_id).all()]
    allowed = department_filter_ids(current_user, all_ids)

    active_headcount = (
        db.query(models.Employee)
        .filter(models.Employee.department_id.in_(allowed), models.Employee.employment_status == "Active")
        .count()
    )
    open_requisitions = (
        db.query(models.Requisition)
        .filter(models.Requisition.department_id.in_(allowed), models.Requisition.job_state == "Open")
        .count()
    )
    total_candidates = db.query(models.Candidate).count()
    hires_to_date = (
        db.query(models.Application)
        .join(models.Requisition, models.Application.requisition_id == models.Requisition.requisition_id)
        .filter(models.Requisition.department_id.in_(allowed), models.Application.workflow_state == "Hired")
        .count()
    )

    return DashboardSummary(
        active_headcount=active_headcount,
        open_requisitions=open_requisitions,
        total_candidates=total_candidates,
        hires_to_date=hires_to_date,
    )
