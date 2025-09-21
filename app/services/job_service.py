from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timezone, timedelta
from app.models.job import Job
from app.models.job_execution import JobExecution
from app.schemas.job_schemas import JobCreate, JobUpdate, JobResponse
from app.services.scheduler_service import SchedulerService
import logging

logger = logging.getLogger(__name__)

class JobService:
    """Service layer for job management operations"""
    
    def __init__(self, db: Session, scheduler_service: SchedulerService):
        self.db = db
        self.scheduler_service = scheduler_service
    
    def create_job(self, job_data: JobCreate, created_by: Optional[str] = None) -> JobResponse:
        """Create a new job and schedule it"""
        try:
            # Calculate next run time
            next_run = self.scheduler_service.calculate_next_run(
                job_data.schedule_type, 
                job_data.schedule_config
            )
            
            # Create job record
            db_job = Job(
                name=job_data.name,
                description=job_data.description,
                job_type=job_data.job_type,
                schedule_type=job_data.schedule_type,
                schedule_config=job_data.schedule_config,
                job_config=job_data.job_config,
                is_active=job_data.is_active,
                next_run=next_run,
                created_by=created_by
            )
            
            self.db.add(db_job)
            self.db.commit()
            self.db.refresh(db_job)
            
            # Schedule the job if active
            if job_data.is_active:
                self.scheduler_service.schedule_job(db_job)
            
            logger.info(f"Created job {db_job.id}: {db_job.name}")
            return JobResponse.from_orm(db_job)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create job: {e}")
            raise
    
    def get_job_by_id(self, job_id: int) -> Optional[JobResponse]:
        """Retrieve a job by its ID"""
        db_job = self.db.query(Job).filter(Job.id == job_id).first()
        if db_job:
            return JobResponse.from_orm(db_job)
        return None
    
    def get_jobs(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        job_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[JobResponse], int]:
        """Retrieve jobs with filtering and pagination"""
        
        query = self.db.query(Job)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Job.is_active == is_active)
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        if search:
            query = query.filter(
                or_(
                    Job.name.ilike(f"%{search}%"),
                    Job.description.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        jobs = query.order_by(desc(Job.created_at)).offset(skip).limit(limit).all()
        
        return [JobResponse.from_orm(job) for job in jobs], total
    
    def update_job(self, job_id: int, job_data: JobUpdate) -> Optional[JobResponse]:
        """Update an existing job"""
        try:
            db_job = self.db.query(Job).filter(Job.id == job_id).first()
            if not db_job:
                return None
            
            # Update fields
            update_data = job_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_job, field, value)
            
            # Recalculate next run if schedule changed
            if 'schedule_config' in update_data:
                next_run = self.scheduler_service.calculate_next_run(
                    db_job.schedule_type,
                    db_job.schedule_config
                )
                db_job.next_run = next_run
            
            db_job.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(db_job)
            
            # Reschedule job
            self.scheduler_service.reschedule_job(db_job)
            
            logger.info(f"Updated job {job_id}")
            return JobResponse.from_orm(db_job)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update job {job_id}: {e}")
            raise
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job"""
        try:
            db_job = self.db.query(Job).filter(Job.id == job_id).first()
            if not db_job:
                return False
            
            # Remove from scheduler
            self.scheduler_service.unschedule_job(job_id)
            
            # Delete job
            self.db.delete(db_job)
            self.db.commit()
            
            logger.info(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete job {job_id}: {e}")
            raise
    
    def get_jobs_for_execution(self) -> List[Job]:
        """Get jobs that are due for execution"""
        now = datetime.now(timezone.utc)
        return self.db.query(Job).filter(
            and_(
                Job.is_active == True,
                Job.next_run <= now
            )
        ).all()
