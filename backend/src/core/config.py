from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_SECRET_KEY: str

    # Jobvite
    JOBVITE_URL: str
    JOBVITE_API_KEY: str
    JOBVITE_API_SECRET: str

    # Dayforce
    DAYFORCE_URL: str | None = None
    DAYFORCE_USERNAME: str | None = None
    DAYFORCE_PASSWORD: str | None = None

    # Scheduled refresh (automated refresh - charter success criterion)
    SYNC_INTERVAL_HOURS: float = 24

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()