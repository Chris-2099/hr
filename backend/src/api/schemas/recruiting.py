from datetime import date
from api.schemas.common import AppBaseModel

class Candidate(AppBaseModel):
    candidate_id: str
    first_name: str
    last_name: str
    email: str | None = None
    work_status: str | None = None
    current_company: str | None = None
    current_title: str | None = None 
    location: str | None = None

class Application(AppBaseModel):
    application_id: str
    source: str | None = None
    workflow_state_id: str | None = None
    workflow_state: str | None = None
    consent_status: str | None = None
    personal_data_processing_status: str | None = None
    sent_date: date | None = None
    last_updated_date: date | None = None
    has_artifacts: bool | None = None

class Requisition(AppBaseModel):
    jobvite_id: str
    requisition_id: str
    title: str
    department_id: str | None = None
    description: str | None = None
    recruiter_email: str | None = None            
    hiring_manager_email: str | None = None       
    job_state: str
    posting_type: str | None = None
    last_update_date: date 
    sent_date: date

class WorkflowState(AppBaseModel):
    workflow_id: str 
    workflow_name: str
    workflow_state_id: str  
    workflow_state_name: str | None = None
    candidate_state_kind: str | None = None
    isInterview: bool | None = None