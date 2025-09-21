from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.services.job_service import JobService
from app.services.scheduler_service import SchedulerService
from app.schemas.job_schemas import (
    JobCreate, JobUpdate, JobResponse, JobListResponse
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    """Dependency to get job service"""
    scheduler_service = SchedulerService()
    return JobService(db, scheduler_service)

# POST jobs
@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    job_service: JobService = Depends(get_job_service)
):
    """Create a new job"""
    try:
        return job_service.create_job(job_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# GET jobs
@router.get("/", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    search: Optional[str] = Query(None, description="Search in job name and description"),
    job_service: JobService = Depends(get_job_service)
):
    """List all jobs with filtering and pagination"""
    jobs, total = job_service.get_jobs(
        skip=skip,
        limit=limit,
        is_active=is_active,
        job_type=job_type,
        search=search
    )
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        has_next=skip + limit < total
    )

# GET job by ID
@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int = Path(..., description="Job ID"),
    job_service: JobService = Depends(get_job_service)
):
    """Get job details by ID"""
    job = job_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# PUT update job
@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int = Path(..., description="Job ID"),
    job_data: JobUpdate = ...,
    job_service: JobService = Depends(get_job_service)
):
    """Update an existing job"""
    job = job_service.update_job(job_id, job_data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# DELETE job
@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: int = Path(..., description="Job ID"),
    job_service: JobService = Depends(get_job_service)
):
    """Delete a job"""
    if not job_service.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
