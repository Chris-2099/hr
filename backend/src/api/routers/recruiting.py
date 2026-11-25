"""Serves Jobvite-shaped ATS data (requisitions, candidates, applications)
with RBAC applied: row-level department scoping on requisitions, column-level
compensation hiding (salary_min/salary_max) for recruiter/viewer - per the
charter's "a recruiter never sees pay data even for their own department's
requisitions" rule."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src import models
from src.api.schemas import ApplicationOut, CandidateOut, RequisitionOut
from src.core.database import get_db
from src.core.deps import CurrentUser, department_filter_ids, get_current_user

router = APIRouter(prefix="/api", tags=["recruiting"])


def _to_requisition_out(req: models.Requisition, can_view_compensation: bool) -> RequisitionOut:
    out = RequisitionOut.model_validate(req)
    if not can_view_compensation:
        out.salary_min = 0
        out.salary_max = 0
    return out


@router.get("/requisitions", response_model=list[RequisitionOut])
def list_requisitions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    all_ids = [d.department_id for d in db.query(models.Department.department_id).all()]
    allowed = department_filter_ids(current_user, all_ids)
    reqs = db.query(models.Requisition).filter(models.Requisition.department_id.in_(allowed)).all()
    return [_to_requisition_out(r, current_user.can_view_compensation) for r in reqs]


@router.get("/candidates", response_model=list[CandidateOut])
def list_candidates(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Candidates aren't department-scoped (a candidate can apply to several
    # requisitions across departments); only applications are.
    candidates = db.query(models.Candidate).all()
    return [CandidateOut.model_validate(c) for c in candidates]


@router.get("/applications", response_model=list[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    all_ids = [d.department_id for d in db.query(models.Department.department_id).all()]
    allowed = department_filter_ids(current_user, all_ids)
    apps = (
        db.query(models.Application)
        .join(models.Requisition, models.Application.requisition_id == models.Requisition.requisition_id)
        .filter(models.Requisition.department_id.in_(allowed))
        .all()
    )
    return [ApplicationOut.model_validate(a) for a in apps]
