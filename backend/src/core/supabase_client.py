from core.config import settings
from supabase import create_client, Client

supabase_url: str = settings.SUPABASE_URL
if not supabase_url:
    raise RuntimeError(
        "Required environment variable SUPABASE_URL is missing."
    )

supabase_key: str = settings.SUPABASE_SECRET_KEY
if not supabase_key:
    raise RuntimeError(
        "Required environment variable SUPABASE_SECRET_KEY is missing."
    )

supabase: Client = create_client(supabase_url, supabase_key)