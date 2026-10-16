# JOBVITE ENDPOINTS ABSTRACTION
import httpx
from api.clients.jobvite_client import JobviteClient
from fastapi import APIRouter, HTTPException
from core.config import settings
from utils.database import SupabaseDatabaseHelper
from utils.pipeline import (
    record_raw_payload, finish_ingestion_run, resolve_status, track_ingestion_run,
    )
from api.schemas.workforce import (
    Department
    )
from api.schemas.recruiting import (
    Requisition, Candidate, Application, WorkflowState,
    )
from utils.utils import (
    html_to_text, timestamp_to_date
    )

router = APIRouter(
    prefix="/api/jobvite",
    tags=["Jobvite"]
)

jobvite_client = JobviteClient(
    base_url=settings.JOBVITE_URL,
    api_key=settings.JOBVITE_API_KEY,
    api_secret=settings.JOBVITE_API_SECRET,
)

@router.get("/health")
def get_health():
    return {"service": "Jobvite API","status":"healthy"}


# ----------------------------
#   API SYNC OPERATIONS
# ----------------------------

@router.post("/job/sync")
async def sync_jobs():
    """ Call Jobvite /job. Place new requistion data into database """
    async with track_ingestion_run(source="jobvite", entity="job") as run_id:
        try:
            response = await jobvite_client.get_jobs()
        except httpx.HTTPStatusError as e:
            # jobvite returned error code
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Jobvite returned an unsuccessful response.",
            ) from e
        except httpx.RequestError as e:
            # couldnt reach jobvite
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Jobvite.",
            ) from e

        record_raw_payload(source="jobvite", entity="job", payload=response)

        # handle data ingestion
        total_reqs = response.get("total", 0)
        jobs = response.get("requisitions", [])
        if not jobs:
            finish_ingestion_run(run_id, resolve_status(total_reqs, 0), total_reqs, 0)
            return {
                "total_requisitions": total_reqs,
                "requisitions": jobs,
                "message": "Jobvite returned no requisition data",
            }

        reqs = []
        for job in jobs:
            data = Requisition(
                jobvite_id=job["eId"],
                requisition_id=job["requisitionId"],
                title=job["title"],
                department_id=job.get("department"),
                description=html_to_text(job.get("description")),
                recruiter_email=job.get("primaryRecruiterEmail"),
                hiring_manager_email=job.get("primaryHiringManagerEmail"),
                job_state=job["jobState"],
                posting_type=job.get("postingType"),
                last_update_date=timestamp_to_date(job["lastUpdatedDate"]),
                sent_date=timestamp_to_date(job["sentDate"]),
            )
            reqs.append(data.model_dump(mode="json"))
        # send data to db
        try:
            SupabaseDatabaseHelper.upsert_records(
                table_name="requisitions",
                records=reqs,
                on_conflict="requisition_id"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to insert into database: {e}",
            ) from e

        finish_ingestion_run(run_id, resolve_status(total_reqs, len(reqs)), total_reqs, len(reqs))
        return {
            "total_requisitions": total_reqs,
            "requisitions": reqs,
        }


@router.post("/candidate/sync")
async def sync_candidates():
    """
    Call Jobvite /candidate. Place new candidate data and related
    application data in database. Application data is attached to
    candidate data in API payload
    """
    async with track_ingestion_run(source="jobvite", entity="candidate") as run_id:
        try:
            response = await jobvite_client.get_candidates()
        except httpx.HTTPStatusError as e:
            # jobvite returned error code
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Jobvite returned an unsuccessful response.",
            ) from e
        except httpx.RequestError as e:
            # couldnt reach jobvite
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Jobvite.",
            ) from e

        record_raw_payload(source="jobvite", entity="candidate", payload=response)

        # handle data ingestion
        candidate_total = response.get("total", 0)
        candidates = response.get("candidates", [])
        if not candidates:
            finish_ingestion_run(run_id, resolve_status(candidate_total, 0), candidate_total, 0)
            return {
                "total_candidates": 0,
                "total_applications": 0,
                "candidates": [],
                "applications": [],
                "message": "Jobvite returned no candidates.",
            }

        apps = []
        cands = []
        for candidate in candidates:
            # map candidate data
            data = Candidate(
                candidate_id=candidate["eId"],
                first_name=candidate["firstName"],
                last_name=candidate["lastName"],
                email=candidate.get("email"),
                work_status=candidate.get("workStatus"),
                current_company=candidate.get("companyName"),
                current_title=candidate.get("title"),
                location=candidate.get("location"),
            )
            cands.append(data.model_dump(mode="json"))
            # map application data
            app = candidate.get("application", {})
            if app.get("eId"):
                data = Application(
                    application_id=app["eId"],
                    source=app.get("source"),
                    workflow_state_id=app.get("workflowStateEId"),
                    workflow_state=app.get("workflowState"),
                    consent_status=app.get("consentStatus"),
                    personal_data_processing_status=app.get("personalDataProcessingStatus"),
                    sent_date=timestamp_to_date(app["sentDate"]),
                    last_updated_date=timestamp_to_date(app["lastUpdatedDate"]),
                    has_artifacts=app.get("hasArtifacts"),
                )
                apps.append(data.model_dump(mode="json"))
        # send data to database
        try:
            # candidates
            SupabaseDatabaseHelper.upsert_records(
                table_name="candidates",
                records=cands,
                on_conflict="candidate_id"
            )
            # applications - don't handle empty payload
            if apps:
                SupabaseDatabaseHelper.upsert_records(
                    table_name="applications",
                    records=apps,
                    on_conflict="application_id"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to insert into database: {e}",
            ) from e

        finish_ingestion_run(run_id, resolve_status(candidate_total, len(cands)), candidate_total, len(cands))
        return {
            "total_candidates": candidate_total,
            "total_applications": len(apps),
            "candidates": cands,
            "applications": apps,
        }

@router.post("/department/sync")
async def sync_departments():
    """
    Call Jobvite /department. Place new department data in database
    """
    async with track_ingestion_run(source="jobvite", entity="department") as run_id:
        try:
            response = await jobvite_client.get_departments()
        except httpx.HTTPStatusError as e:
            # jobvite returned error code
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Jobvite returned an unsuccessful response.",
            ) from e
        except httpx.RequestError as e:
            # couldnt reach jobvite
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Jobvite.",
            ) from e

        record_raw_payload(source="jobvite", entity="department", payload=response)

        # handle data ingestion
        totalDepts = response.get("total", 0)
        departments = response.get("departments", [])
        if not departments:
            finish_ingestion_run(run_id, resolve_status(totalDepts, 0), totalDepts, 0)
            return {
                "total_departments": totalDepts,
                "departments": [],
                "message": "Jobvite returned no department data",
            }

        depts = []
        for department in departments:
            data = Department(
                jobvite_id = department["eId"],
                department_id = department["eId"],
                department_name = department["name"],
            )
            depts.append(data.model_dump(mode="json"))
        # send data to db
        try:
            SupabaseDatabaseHelper.upsert_records(
                table_name="departments",
                records=depts,
                on_conflict="department_id"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to insert into database: {e}",
            ) from e

        finish_ingestion_run(run_id, resolve_status(totalDepts, len(depts)), totalDepts, len(depts))
        return {
            "total_departments": totalDepts,
            "departments": depts,
        }


@router.post("/workflow/sync")
async def sync_workflows():
    """
    Call Jobvite /workflow. Place new workflow data in database
    """
    async with track_ingestion_run(source="jobvite", entity="workflow") as run_id:
        try:
            response = await jobvite_client.get_workflows()
        except httpx.HTTPStatusError as e:
            # jobvite returned error code
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Jobvite returned an unsuccessful response.",
            ) from e
        except httpx.RequestError as e:
            # couldnt reach jobvite
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Jobvite.",
            ) from e

        record_raw_payload(source="jobvite", entity="workflow", payload=response)

        # handle data ingestion
        totalWorkflows = response.get("total", 0)
        workflows = response.get("workflows", [])
        if not workflows:
            finish_ingestion_run(run_id, resolve_status(totalWorkflows, 0), totalWorkflows, 0)
            return {
                "total_workflows": totalWorkflows,
                "workflow": workflows,
                "message": "Jobvite returned no workflow data",
            }

        workflow_states = []
        for workflow in workflows:
            workflow_id = workflow["eId"]
            workflow_name = workflow["name"]

            for state in workflow.get("states", []):
                workflow_states.append(
                    WorkflowState(
                        workflow_id=workflow_id,
                        workflow_name=workflow_name,
                        workflow_state_id=state["eId"],
                        workflow_state_name=state["name"],
                        candidate_state_kind=state.get("candidateStateKind"),
                        isInterview=state.get("isInterview"),
                    ).model_dump(mode="json")
                )

        # send data to db
        try:
            SupabaseDatabaseHelper.upsert_records(
                table_name="workflow_states",
                records=workflow_states,
                on_conflict="workflow_state_id"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to insert into database: {e}",
            ) from e

        # reported total is a count of workflows, not states, so validate
        # against len(workflows) (the matching unit) rather than states count
        finish_ingestion_run(
            run_id,
            resolve_status(totalWorkflows, len(workflows)),
            totalWorkflows,
            len(workflows),
        )
        return {
            "total_workflows": totalWorkflows,
            "workflow": workflows,
            "workflow_states": workflow_states,
        }
