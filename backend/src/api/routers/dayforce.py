# DAYFORCE ENDPOINTS ABSTRACTION
#
# ** PROVISIONAL ** - see api/clients/dayforce_client.py for what's verified
# vs. assumed. _map_employee() below is a best-guess field mapping built from
# commonly-documented Dayforce field names (XRefCode, FirstName, LastName,
# HireDate, TerminationDate, EmploymentStatus, ManagerXRefCode) and is the
# part most likely to need correction once real API access lands - everything
# else in this file (auth, raw capture, run tracking, upsert) should not need
# to change.
import httpx
from api.clients.dayforce_client import DayforceClient
from fastapi import APIRouter, HTTPException
from core.config import settings
from utils.database import SupabaseDatabaseHelper
from utils.pipeline import (
    record_raw_payload, finish_ingestion_run, resolve_status, track_ingestion_run,
    )
from api.schemas.workforce import Employee

router = APIRouter(
    prefix="/api/dayforce",
    tags=["Dayforce"]
)

dayforce_client = (
    DayforceClient(
        base_url=settings.DAYFORCE_URL,
        username=settings.DAYFORCE_USERNAME,
        password=settings.DAYFORCE_PASSWORD,
    )
    if settings.DAYFORCE_URL and settings.DAYFORCE_USERNAME and settings.DAYFORCE_PASSWORD
    else None
)


@router.get("/health")
def get_health():
    return {"Status": "Active"}


def _map_employee(raw: dict) -> Employee:
    """
    PROVISIONAL field mapping - unverified against a real Dayforce payload.
    Adjust field names here once the actual API Explorer response is seen;
    nothing else in this router should need to change.
    """
    return Employee(
        employee_id=raw["XRefCode"],
        first_name=raw["FirstName"],
        last_name=raw["LastName"],
        email=raw.get("HomeEmail") or raw.get("WorkEmail"),
        department=raw.get("Department"),
        manager_id=raw.get("ManagerXRefCode"),
        roles=raw.get("Position"),
        start_date=raw.get("HireDate"),
        employment_status=raw["EmploymentStatus"],
        employee_type=raw.get("EmployeeType"),
    )


# ----------------------------
#   API SYNC OPERATIONS
# ----------------------------

@router.post("/employee/sync")
async def sync_employees():
    """ Call Dayforce GET /Employees. Place employee master data into database. """
    if dayforce_client is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Dayforce is not configured yet - set DAYFORCE_URL, "
                "DAYFORCE_USERNAME, and DAYFORCE_PASSWORD."
            ),
        )

    async with track_ingestion_run(source="dayforce", entity="employee") as run_id:
        try:
            response = await dayforce_client.get_employees()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Dayforce returned an unsuccessful response.",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Dayforce.",
            ) from e

        record_raw_payload(source="dayforce", entity="employee", payload=response)

        # UNVERIFIED: assumes a bare list; Dayforce may wrap this (e.g. under
        # "Data") - confirm against the real response and adjust.
        raw_employees = response if isinstance(response, list) else response.get("Data", [])
        total = len(raw_employees)
        if not raw_employees:
            finish_ingestion_run(run_id, resolve_status(total, 0), total, 0)
            return {
                "total_employees": 0,
                "employees": [],
                "message": "Dayforce returned no employee data",
            }

        employees = [_map_employee(raw).model_dump(mode="json") for raw in raw_employees]

        try:
            SupabaseDatabaseHelper.upsert_records(
                table_name="employees",
                records=employees,
                on_conflict="employee_id",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to insert into database: {e}",
            ) from e

        finish_ingestion_run(run_id, resolve_status(total, len(employees)), total, len(employees))
        return {
            "total_employees": total,
            "employees": employees,
        }
