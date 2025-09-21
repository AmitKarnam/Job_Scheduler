from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn

from app.config.settings import settings
from app.api.routes import jobs
from app.api.routes import healthcheck
from app.services.scheduler_service import SchedulerService
from app.models.job import Base
from app.database.connection import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global scheduler_service
    
    # Startup
    logger.info("Starting Job Scheduler Microservice")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize and start scheduler
    scheduler_service = SchedulerService()
    scheduler_service.start()
    
    # Load and schedule existing active jobs
    from app.database.connection import get_db_context
    from app.models.job import Job
    
    with get_db_context() as db:
        active_jobs = db.query(Job).filter(Job.is_active == True).all()
        for job in active_jobs:
            try:
                scheduler_service.schedule_job(job)
                logger.info(f"Rescheduled job {job.id}: {job.name}")
            except Exception as e:
                logger.error(f"Failed to reschedule job {job.id}: {e}")
    
    logger.info("Scheduler service started successfully")
    
    yield
    
    # Shutdown
    if scheduler_service:
        scheduler_service.shutdown()
    logger.info("Job Scheduler Microservice stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(healthcheck.router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Job Scheduler Microservice",
        "version": settings.api_version,
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1  # Use 1 worker for development, increase for production
    )
