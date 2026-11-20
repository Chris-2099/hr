"""Pulls data from Jobvite and upserts it into the local database.

Pairs with src/api/clients/jobvite_client.py (the raw HTTP calls) and
src/api/clients/jobvite_mapper.py (raw JSON -> our column names) - this
module is the orchestration layer: call the client, map the response,
resolve foreign keys, upsert, log the attempt.

    python -m src.api.jobvite                       # run every step once
    python -m src.api.jobvite requisitions          # run one step
    python -m src.api.jobvite interviews <app_id>   # interviews needs an application id

None of these have ever succeeded end-to-end - there are no real Jobvite
credentials yet (see backend/.env.example) - so running this today logs a
clean failure per step and exits 0. Once real credentials land in `.env`,
this becomes the real pipeline with no further code needed for the happy
path.
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging

from sqlalchemy.orm import Session

from src import models
from src.core.database import SessionLocal
from src.api.clients.jobvite_client import JobviteClient, JobviteError
from src.api.clients.jobvite_mapper import (
    map_candidate_and_application,
    map_interview_slots,
    map_requisition,
)

logger = logging.getLogger(__name__)


def _log_run(db: Session, entity: str, status: str, count: int, notes: str) -> None:
    db.add(
        models.IngestionRun(
            source_system="jobvite",
            entity=entity,
            started_at=dt.datetime.utcnow(),
            completed_at=dt.datetime.utcnow(),
            status=status,
            records_processed=count,
            notes=notes[:2000],
        )
    )
    db.commit()


def sync_requisitions(db: Session) -> dict:
    client = JobviteClient()
    try:
        raw = client.get_requisitions(count=100)
    except JobviteError as exc:
        _log_run(db, "requisitions", "failure", 0, str(exc))
        return {"processed": 0, "error": str(exc)}

    processed = 0
    skipped: list[str] = []
    for item in raw.get("jobs", raw.get("requisitions", [])):
        mapped = map_requisition(item)
        dept = (
            db.query(models.Department).filter(models.Department.name == mapped["department_name"]).first()
            if mapped["department_name"]
            else None
        )
        loc = (
            db.query(models.Location).filter(models.Location.name == mapped["location_name"]).first()
            if mapped["location_name"]
            else None
        )
        if not dept or not loc or not mapped["jobvite_eid"]:
            skipped.append(mapped.get("jobvite_eid") or "unknown")
            continue
        existing = db.query(models.Requisition).filter(models.Requisition.jobvite_eid == mapped["jobvite_eid"]).first()
        row = existing or models.Requisition(
            requisition_id=mapped["jobvite_eid"], jobvite_eid=mapped["jobvite_eid"],
            hiring_manager_employee_id="", recruiter_employee_id="", opened_date=dt.date.today(),
        )
        row.title = mapped["title"]
        row.department_id = dept.department_id
        row.location_id = loc.location_id
        row.job_state = mapped["job_state"]
        row.category = mapped["category"]
        row.eeo_category = mapped["eeo_category"]
        row.posting_type = mapped["posting_type"]
        row.remote_type = mapped["remote_type"]
        row.position_count = mapped["position_count"]
        row.salary_min = mapped["salary_min"] or 0
        row.salary_max = mapped["salary_max"] or 0
        row.salary_currency = mapped["salary_currency"]
        row.salary_frequency = mapped["salary_frequency"]
        if not existing:
            db.add(row)
        processed += 1
    db.commit()

    notes = f"Mapped {processed} requisition(s); skipped {len(skipped)} (unresolved department/location/eid)."
    _log_run(db, "requisitions", "success", processed, notes)
    return {"processed": processed, "skipped": skipped}


def sync_candidates(db: Session) -> dict:
    client = JobviteClient()
    try:
        raw = client.get_candidates(count=100)
    except JobviteError as exc:
        _log_run(db, "candidates", "failure", 0, str(exc))
        return {"processed": 0, "error": str(exc)}

    processed = 0
    skipped: list[str] = []
    for item in raw.get("candidates", []):
        cand_fields, app_fields = map_candidate_and_application(item)
        if not cand_fields["jobvite_eid"]:
            continue
        existing = db.query(models.Candidate).filter(models.Candidate.jobvite_eid == cand_fields["jobvite_eid"]).first()
        row = existing or models.Candidate(candidate_id=cand_fields["jobvite_eid"], jobvite_eid=cand_fields["jobvite_eid"])
        for field in ("first_name", "last_name", "email", "city", "state", "postal_code", "country",
                      "current_title", "current_company_name", "work_status", "veteran_status",
                      "source", "source_type", "gender", "race_ethnicity"):
            setattr(row, field, cand_fields[field])
        if not existing:
            db.add(row)

        req = (
            db.query(models.Requisition)
            .filter(models.Requisition.jobvite_eid == app_fields["requisition_jobvite_eid"])
            .first()
            if app_fields["requisition_jobvite_eid"]
            else None
        )
        if not req or not app_fields["jobvite_application_eid"]:
            skipped.append(cand_fields["jobvite_eid"])
            processed += 1  # candidate row still upserted even if application can't be linked
            continue

        app_id = app_fields["jobvite_application_eid"]
        existing_app = db.query(models.Application).filter(models.Application.application_id == app_id).first()
        app_row = existing_app or models.Application(
            application_id=app_id, candidate_id=row.candidate_id, requisition_id=req.requisition_id,
            workflow_state=app_fields["workflow_state"] or "New",
            workflow_state_eid=app_fields["workflow_state_eid"] or "",
            applied_date=app_fields["applied_date"] or dt.date.today(),
        )
        app_row.workflow_state = app_fields["workflow_state"] or app_row.workflow_state
        app_row.workflow_state_eid = app_fields["workflow_state_eid"] or app_row.workflow_state_eid
        app_row.disposition = app_fields["disposition"]
        app_row.hire_date = app_fields["hire_date"]
        app_row.start_date = app_fields["start_date"]
        if not existing_app:
            db.add(app_row)
        processed += 1
    db.commit()

    notes = f"Mapped {processed} candidate(s); {len(skipped)} with an application that couldn't be linked to a known requisition."
    _log_run(db, "candidates", "success", processed, notes)
    return {"processed": processed, "unlinked_applications": skipped}


def sync_interviews(db: Session, application_id: str) -> dict:
    client = JobviteClient()
    try:
        raw = client.get_interviews(application_id=application_id)
    except JobviteError as exc:
        _log_run(db, "interviews", "failure", 0, str(exc))
        return {"processed": 0, "error": str(exc)}

    slots = map_interview_slots(raw)
    processed = 0
    for slot in slots:
        if not slot["jobvite_interview_eid"] or not slot["application_jobvite_eid"]:
            continue
        existing = (
            db.query(models.Interview)
            .filter(models.Interview.jobvite_interview_eid == slot["jobvite_interview_eid"])
            .first()
        )
        row = existing or models.Interview(
            interview_id=slot["jobvite_interview_eid"],
            jobvite_interview_eid=slot["jobvite_interview_eid"],
            application_id=slot["application_jobvite_eid"],
            interviewer_employee_id=slot["interviewer_jobvite_user_eid"] or "",
            scheduled_date=slot["scheduled_date"] or dt.date.today(),
            duration_minutes=slot["duration_minutes"] or 30,
            stage="Panel",
        )
        row.timezone = slot["timezone"]
        row.evaluation_link = slot["evaluation_link"]
        row.status = slot["status"]
        if not existing:
            db.add(row)
        processed += 1
    db.commit()

    _log_run(db, "interviews", "success", processed, f"Mapped {processed} interview slot(s) for application {application_id}.")
    return {"processed": processed}


def run_all() -> None:
    """requisitions + candidates only - interviews needs a specific
    application_id, not a blanket "sync everything" call."""
    db = SessionLocal()
    try:
        logger.info("requisitions: %s", sync_requisitions(db))
        logger.info("candidates: %s", sync_candidates(db))
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "step",
        nargs="?",
        choices=["requisitions", "candidates", "interviews"],
        help="Run a single step instead of all of them.",
    )
    parser.add_argument("application_id", nargs="?", help="Required when step=interviews.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.step == "interviews":
        if not args.application_id:
            parser.error("interviews requires an application_id")
        db = SessionLocal()
        try:
            logger.info("interviews: %s", sync_interviews(db, args.application_id))
        finally:
            db.close()
    elif args.step:
        db = SessionLocal()
        try:
            fn = {"requisitions": sync_requisitions, "candidates": sync_candidates}[args.step]
            logger.info("%s: %s", args.step, fn(db))
        finally:
            db.close()
    else:
        run_all()


if __name__ == "__main__":
    main()
