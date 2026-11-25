"""Admin-only routes that trigger the pipeline (src/api/jobvite.py,
src/api/dayforce.py) over HTTP instead of the CLI - same functions either
way, no ingestion logic duplicated here."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src import models
from src.api import dayforce, jobvite
from src.core.config import settings
from src.core.database import get_db
from src.core.deps import CurrentUser, require_roles

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/status")
def integration_status(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    """Recent sync attempts + whether each system has non-placeholder credentials configured."""
    runs = db.query(models.IngestionRun).order_by(models.IngestionRun.started_at.desc()).limit(20).all()
    return {
        "configured": {
            "jobvite": bool(settings.JOBVITE_API_KEY) and "placeholder" not in settings.JOBVITE_API_KEY.lower(),
            "dayforce": bool(settings.DAYFORCE_USERNAME) and "placeholder" not in settings.DAYFORCE_USERNAME.lower(),
        },
        "recent_runs": [
            {
                "source_system": r.source_system,
                "entity": r.entity,
                "status": r.status,
                "records_processed": r.records_processed,
                "started_at": r.started_at.isoformat(),
                "notes": r.notes,
            }
            for r in runs
        ],
    }


@router.post("/jobvite/sync/departments")
def sync_jobvite_departments(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    return jobvite.sync_departments(db)


@router.post("/jobvite/sync/requisitions")
def sync_jobvite_requisitions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    return jobvite.sync_requisitions(db)


@router.post("/jobvite/sync/candidates")
def sync_jobvite_candidates(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    return jobvite.sync_candidates(db)


@router.post("/jobvite/sync/interviews")
def sync_jobvite_interviews(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    return jobvite.sync_interviews(db, application_id)


@router.post("/dayforce/sync/employees")
def sync_dayforce_employees(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    return dayforce.sync_employees(db)
