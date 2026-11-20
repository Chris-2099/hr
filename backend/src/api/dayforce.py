"""Pulls data from Dayforce and upserts it into the local database.

Pairs with src/api/clients/dayforce_client.py (the raw HTTP calls) and
src/api/clients/dayforce_mapper.py (raw JSON -> our column names) - this
module is the orchestration layer: call the client, map the response,
upsert, log the attempt.

    python -m src.api.dayforce              # run every step once
    python -m src.api.dayforce employees    # run one step

None of these have ever succeeded end-to-end - there are no real Dayforce
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
from src.api.clients.dayforce_client import DayforceClient, DayforceError
from src.api.clients.dayforce_mapper import map_employee

logger = logging.getLogger(__name__)


def _log_run(db: Session, entity: str, status: str, count: int, notes: str) -> None:
    db.add(
        models.IngestionRun(
            source_system="dayforce",
            entity=entity,
            started_at=dt.datetime.utcnow(),
            completed_at=dt.datetime.utcnow(),
            status=status,
            records_processed=count,
            notes=notes[:2000],
        )
    )
    db.commit()


def sync_employees(db: Session) -> dict:
    """Base Employee fields only (confirmed shape). Department/position/
    location/manager/employment_status require WorkAssignments, whose field
    names are unverified (see dayforce_mapper.py) - not attempted here to
    avoid writing guessed data into those columns."""
    client = DayforceClient()
    try:
        raw = client.get_employees()
    except DayforceError as exc:
        _log_run(db, "employees", "failure", 0, str(exc))
        return {"processed": 0, "error": str(exc)}

    processed = 0
    for item in raw.get("Data", []):
        mapped = map_employee(item)
        if not mapped["dayforce_employee_id"]:
            continue
        existing = (
            db.query(models.Employee)
            .filter(models.Employee.dayforce_employee_id == mapped["dayforce_employee_id"])
            .first()
        )
        if not existing:
            # Can't create a full Employee row yet - department_id/position_id/
            # location_id are required (NOT NULL) and only resolvable via
            # WorkAssignments, which isn't implemented (see docstring above).
            continue
        existing.first_name = mapped["first_name"] or existing.first_name
        existing.last_name = mapped["last_name"] or existing.last_name
        existing.birth_date = mapped["birth_date"] or existing.birth_date
        existing.gender = mapped["gender"] or existing.gender
        existing.hire_date = mapped["hire_date"] or existing.hire_date
        processed += 1
    db.commit()

    notes = f"Updated {processed} existing employee(s)' base fields. New-hire creation needs WorkAssignments mapping first."
    _log_run(db, "employees", "success", processed, notes)
    return {"processed": processed}


def run_all() -> None:
    db = SessionLocal()
    try:
        logger.info("employees: %s", sync_employees(db))
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "step",
        nargs="?",
        choices=["employees"],
        help="Run a single step instead of all of them.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.step:
        db = SessionLocal()
        try:
            logger.info("%s: %s", args.step, sync_employees(db))
        finally:
            db.close()
    else:
        run_all()


if __name__ == "__main__":
    main()
