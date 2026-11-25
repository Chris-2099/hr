from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import Base, engine
from src.api.routers import admin, auth, dashboard, employees, integrations, recruiting


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="HR Workforce & Org Health Dashboard API",
        version="0.2.0",
        description="Internal workforce intelligence API backed by Jobvite/Dayforce-shaped data.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(employees.router)
    app.include_router(recruiting.router)
    app.include_router(dashboard.router)
    app.include_router(admin.router)
    app.include_router(integrations.router)

    @app.get("/")
    def root():
        return {"service": "HR Workforce & Org Health Dashboard API", "status": "healthy"}

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    return app


app = create_app()
