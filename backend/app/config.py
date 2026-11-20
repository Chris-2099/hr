from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "local"
    DATABASE_URL: str = "sqlite:///./hr_dashboard.db"

    # Source system credentials for the ingestion pipeline (app/sync.py).
    JOBVITE_API_URL: str = ""
    JOBVITE_API_KEY: str = ""
    JOBVITE_API_SECRET: str = ""
    DAYFORCE_API_URL: str = ""  # e.g. https://usXX.dayforcehcm.com/api/{clientNamespace}/V1
    DAYFORCE_TOKEN_URL: str = "https://dfid.dayforcehcm.com/connect/token"
    DAYFORCE_CLIENT_NAMESPACE: str = ""  # companyId
    DAYFORCE_USERNAME: str = ""
    DAYFORCE_PASSWORD: str = ""
    DAYFORCE_CLIENT_ID: str = "Dayforce.HCMAnywhere.Client"  # fixed per Dayforce's own docs

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
