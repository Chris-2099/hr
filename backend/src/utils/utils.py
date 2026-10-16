from datetime import date, datetime, timezone
from bs4 import BeautifulSoup
from utils.database import SupabaseDatabaseHelper
from fastapi import HTTPException
import html

def html_to_text(value: str | None) -> str | None:
    """Convert encoded HTML into plain text."""
    if not value:
        return None
    decoded_html = html.unescape(value)
    soup = BeautifulSoup(decoded_html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def timestamp_to_date(value: int | None) -> date | None:
    """Convert a Unix millisecond timestamp into a UTC date."""
    if value is None:
        return None
    return datetime.fromtimestamp(
        value / 1000,
        tz=timezone.utc,
    ).date()

def get_table_records(
    table_name: str,
    resource_name: str,
) -> dict:
    """Retrieve records from Supabase and format the API response."""

    try:
        db_response = SupabaseDatabaseHelper.get_records(table_name)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve {resource_name} from database: {e}",
        ) from e

    records = db_response.data

    if records is None:
        raise HTTPException(
            status_code=500,
            detail="Database returned an invalid response.",
        )

    return {
        f"total_{resource_name}": len(records),
        resource_name: records,
    }

