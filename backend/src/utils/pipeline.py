# PIPELINE HELPERS: raw payload capture, ingestion run tracking, validation.
#
# Tables live in the `pipeline` Postgres schema (see database.sql). That
# schema must be added under Project Settings > API > Exposed schemas in the
# Supabase dashboard before these calls will succeed.
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from core.supabase_client import supabase


def record_raw_payload(source: str, entity: str, payload: Any) -> None:
    """Store an untouched copy of a source API response before transforming it."""
    supabase.schema("pipeline").table("raw_payloads").insert({
        "source": source,
        "entity": entity,
        "payload": payload,
    }).execute()


def start_ingestion_run(source: str, entity: str) -> int:
    """Record the start of a sync call. Returns the run_id to finish later."""
    response = (
        supabase.schema("pipeline")
        .table("ingestion_runs")
        .insert({"source": source, "entity": entity, "status": "running"})
        .execute()
    )
    return response.data[0]["run_id"]


def finish_ingestion_run(
    run_id: int,
    status: str,
    reported_total: int | None = None,
    rows_processed: int | None = None,
    error: str | None = None,
) -> None:
    """Close out a run with its outcome. status: 'success' | 'partial' | 'failed'."""
    supabase.schema("pipeline").table("ingestion_runs").update({
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "reported_total": reported_total,
        "rows_processed": rows_processed,
        "error": error,
    }).eq("run_id", run_id).execute()


def resolve_status(reported_total: int | None, rows_processed: int) -> str:
    """
    Compare what the source said it had against what was actually processed.
    Anything less than reported is 'partial', not silently 'success' — this
    is the only thing currently standing in for the charter's accuracy check.
    """
    if reported_total is None:
        return "success"
    if rows_processed >= reported_total:
        return "success"
    return "partial"


@asynccontextmanager
async def track_ingestion_run(source: str, entity: str) -> AsyncIterator[int]:
    """
    Wrap a sync endpoint body. Marks the run 'failed' and records the error
    automatically if anything inside raises (including an HTTPException from
    source-connection errors) — callers only need to call
    finish_ingestion_run() themselves on the success/partial path.
    """
    run_id = start_ingestion_run(source, entity)
    try:
        yield run_id
    except Exception as e:
        finish_ingestion_run(run_id, status="failed", error=str(e))
        raise
