"""Maps raw Jobvite API v2 JSON into flat dicts matching our column names.

These are pure functions (raw dict -> normalized dict) - no DB access, no
FK resolution. Resolving a mapped record's department/location/requisition
to our internal ids is the sync routes' job (app/routers/integrations.py),
since that needs a DB session. Field names here are taken directly from the
"Response Specifications" tables in Jobvite-API-v2 04122025.pdf; never run
against a live payload, so treat as a strong first draft, not verified.
"""

from __future__ import annotations

import datetime as dt


def epoch_ms_to_date(value) -> dt.date | None:
    if value is None:
        return None
    try:
        return dt.datetime.utcfromtimestamp(int(value) / 1000).date()
    except (TypeError, ValueError):
        return None


def map_candidate_and_application(raw: dict) -> tuple[dict, dict]:
    """One element of GET /candidate's `candidates` array -> (candidate_fields, application_fields)."""
    app = raw.get("application") or {}
    job = app.get("job") or {}

    candidate_fields = {
        "jobvite_eid": raw.get("eId"),
        "first_name": raw.get("firstName"),
        "last_name": raw.get("lastName"),
        "email": raw.get("email"),
        "city": raw.get("city"),
        "state": raw.get("state"),
        "postal_code": raw.get("postalCode"),
        "country": raw.get("country") or raw.get("countryName"),
        "current_title": raw.get("title"),
        "current_company_name": raw.get("companyName"),
        "work_status": raw.get("workStatus") or "None",
        "veteran_status": app.get("veteranStatus") or "Not a Veteran",
        "source": app.get("source") or "",
        "source_type": app.get("sourceType") or "",
    }

    application_fields = {
        "jobvite_application_eid": app.get("eId"),
        "workflow_state": app.get("workflowState"),
        "workflow_state_eid": app.get("workflowStateEId"),
        "disposition": app.get("disposition"),
        "applied_date": epoch_ms_to_date(app.get("sentDate")),
        "hire_date": epoch_ms_to_date(app.get("hireDate")),
        "start_date": epoch_ms_to_date(app.get("startDate")),
        "consent_status": app.get("consentStatus"),
        "personal_data_processing_status": app.get("personalDataProcessingStatus"),
        "has_artifacts": app.get("hasArtifacts"),
        # resolved against requisitions.jobvite_eid by the sync route, not here
        "requisition_jobvite_eid": job.get("eId"),
    }
    return candidate_fields, application_fields


def map_department(raw: dict) -> dict:
    """One element of GET /department's `departments` array -> fields to
    match against an existing (Dayforce-sourced) Department by name and
    attach a jobvite_id to. Jobvite's /department endpoint doesn't carry
    enough to create a full Department row on its own (no org hierarchy,
    no Dayforce xref) - see sync_departments in src/api/jobvite.py."""
    return {
        "jobvite_eid": raw.get("eId"),
        "department_name": raw.get("name"),
    }


def map_requisition(raw: dict) -> dict:
    """One element of GET /job's job list -> Requisition fields (department/location
    are returned to the sync route as names to resolve, not ids)."""
    return {
        "jobvite_eid": raw.get("eId"),
        "title": raw.get("title"),
        "department_name": raw.get("department"),
        "location_name": raw.get("location"),
        "job_state": raw.get("jobState"),
        "category": raw.get("category"),
        "eeo_category": raw.get("eeoCategory"),
        "posting_type": raw.get("postingType") or "External",
        "remote_type": raw.get("remoteType") or "Onsite",
        "position_count": raw.get("positionCount") or 1,
        "salary_min": raw.get("salaryMin"),
        "salary_max": raw.get("salaryMax"),
        "salary_currency": raw.get("salaryCurrency") or "USD",
        "salary_frequency": raw.get("salaryFrequency") or "Annually",
        "requisition_id": raw.get("requisitionId"),  # customer-facing req number, if auto-numbering is on
    }


def map_interview_slots(raw: dict) -> list[dict]:
    """GET /interview's response (one block, with nested interviewer slots)
    -> one flat dict per interviewer/slot."""
    application_eid = raw.get("applicationEId")
    workflow_state_eid = raw.get("workflowStateEId")
    out = []
    for slot in raw.get("interviews", []) or []:
        for interviewer in slot.get("interviewers", []) or []:
            out.append(
                {
                    "jobvite_interview_eid": interviewer.get("interviewEId"),
                    "application_jobvite_eid": application_eid,
                    "workflow_state_eid": workflow_state_eid,
                    "interviewer_jobvite_user_eid": interviewer.get("userEId") or interviewer.get("eId"),
                    "scheduled_date": epoch_ms_to_date(slot.get("startTime")),
                    "duration_minutes": slot.get("duration"),
                    "timezone": interviewer.get("timezone") or "America/Los_Angeles",
                    "evaluation_link": interviewer.get("evaluationLink") or "",
                    "status": interviewer.get("status") or "Schedule",
                }
            )
    return out
