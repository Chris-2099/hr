# JOBVITE ENDPOINTS ABSTRACTION
from utils.utils import ( get_table_records )
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/database",
    tags=["Database"]
)

# ----------------------------
#   DATABASE OPERATIONS
# ----------------------------
@router.get("/jobs")
async def get_requistions():
    """ read requisition data from database """
    return get_table_records(
        table_name="requisitions",
        resource_name="requisitions",
    )

@router.get("/candidates")
async def get_candidates():
    """ read candidate data from database """
    return get_table_records(
        table_name="candidates",
        resource_name="candidates",
    )

@router.get("/applications")
async def get_applications():
    """ read application data from database """
    return get_table_records(
        table_name="applications",
        resource_name="applications",
    )

@router.get("/departments")
async def get_departments():
    """ read department data from database """
    return get_table_records(
        table_name="departments",
        resource_name="departments",
    )

@router.get("/workflows")
async def get_departments():
    """ read workflow state data from database """
    return get_table_records(
        table_name="workflow_states",
        resource_name="workflow_states",
    )
