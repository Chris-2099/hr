import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routers.dayforce import router as dayforceRouter
from api.routers.jobvite import router as jobviteRouter
from core.supabase_client import supabase
from core.scheduler import create_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application!")
    # verify Supabase is reachable
    try:
        supabase.table("departments").select("*").limit(1).execute()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

    scheduler = create_scheduler()
    scheduler.start()
    print("Scheduled refresh started")

    yield

    scheduler.shutdown()
    print("Shutting down application!")

# intialize project
def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(dayforceRouter);
    app.include_router(jobviteRouter);
    return app

app = create_app()

# internal endpoints
@app.get("/")
def root():
    return {
        "service": "HR Intelligence Platform",
        "version": "v1.0",
        "status": "healthy"
    }

@app.get("/health")
def health():   
    return {
        "service": "HR Intelligence Platform",
        "status":"healthy"
    }

# page specific endpoints
# @app.get("/talent_acquisition")
# def talentAcquistion():


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)