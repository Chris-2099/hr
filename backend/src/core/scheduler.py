# AUTOMATED REFRESH (charter success criterion). Calls the same sync
# functions the manual POST endpoints call, on an interval, so refresh
# doesn't depend on someone remembering to trigger it by hand.
#
# This is an in-process scheduler - it only runs while the FastAPI app is
# running. If deployment moves to something that scales to zero or runs
# multiple replicas, replace this with an external scheduler (cron, GitHub
# Actions, Supabase scheduled functions) calling the sync endpoints over
# HTTP instead, so a sync doesn't get triggered once per replica.
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.config import settings
from api.routers.jobvite import sync_jobs, sync_candidates, sync_departments, sync_workflows
from api.routers.dayforce import sync_employees

SYNC_JOBS = [
    ("jobvite_jobs", sync_jobs),
    ("jobvite_candidates", sync_candidates),
    ("jobvite_departments", sync_departments),
    ("jobvite_workflows", sync_workflows),
    ("dayforce_employees", sync_employees),
]


async def _run_sync(name: str, sync_fn) -> None:
    try:
        await sync_fn()
    except Exception as e:
        # Each sync_fn already records its own failure in pipeline.ingestion_runs;
        # this print is just so a failure is visible in process logs too.
        print(f"Scheduled sync '{name}' failed: {e}")


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    for name, sync_fn in SYNC_JOBS:
        scheduler.add_job(
            _run_sync,
            trigger="interval",
            hours=settings.SYNC_INTERVAL_HOURS,
            args=[name, sync_fn],
            id=name,
            replace_existing=True,
        )
    return scheduler
