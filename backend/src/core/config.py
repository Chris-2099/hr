from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "local"
    DATABASE_URL: str = "sqlite:///./hr_dashboard.db"
    SECRET_KEY: str = "change-me-dev-only-not-for-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    # Comma-separated list. Defaults cover local Vite dev; set explicitly in prod.
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # DEV ONLY. When true, every request is auto-authenticated as
    # DEV_DEFAULT_USER_EMAIL (or whoever the X-Dev-User-Email header names)
    # with no token/login required - so local testing/dashboard work isn't
    # blocked on wiring up a login screen. Must be false before any real
    # deployment - see core/deps.py:get_current_user(). Defaults true so
    # this build runs login-free out of the box.
    DISABLE_AUTH: bool = True
    DEV_DEFAULT_USER_EMAIL: str = "admin"

    # SSO (Entra ID) - wired but dormant. AUTH_MODE stays "local" until a
    # real Entra App Registration exists; "hybrid" would add Microsoft
    # sign-in alongside local login, "entra" would require it. The frontend
    # reads this via GET /api/auth/config and only enables its "Sign in
    # with Microsoft" button when this isn't "local" - see
    # src/api/routers/auth.py and frontend/src/pages/Login.tsx.
    AUTH_MODE: str = "local"  # local | entra | hybrid
    ENTRA_TENANT_ID: str = ""
    ENTRA_CLIENT_ID: str = ""
    ENTRA_CLIENT_SECRET: str = ""
    ENTRA_REDIRECT_URI: str = ""

    # Source system credentials for the ingestion pipeline (src/api/jobvite.py,
    # src/api/dayforce.py).
    JOBVITE_URL: str = ""
    JOBVITE_API_KEY: str = ""
    JOBVITE_API_SECRET: str = ""
    DAYFORCE_URL: str = ""  # e.g. https://usXX.dayforcehcm.com/api/{clientNamespace}/V1
    DAYFORCE_TOKEN_URL: str = "https://dfid.dayforcehcm.com/connect/token"
    DAYFORCE_CLIENT_NAMESPACE: str = ""  # companyId
    DAYFORCE_USERNAME: str = ""
    DAYFORCE_PASSWORD: str = ""
    DAYFORCE_CLIENT_ID: str = "Dayforce.HCMAnywhere.Client"  # fixed per Dayforce's own docs

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
