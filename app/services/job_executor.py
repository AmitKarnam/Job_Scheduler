import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.job_execution import JobExecution
from app.database.connection import get_db_context
from app.services.job_handler import JobHandlerFactory
import logging

logger = logging.getLogger(__name__)

class JobExecutor:
    """Service for executing scheduled jobs"""
    
    @staticmethod
    def execute_job(job_id: int) -> Dict[str, Any]:
        """Execute a job and record the execution"""
        
        with get_db_context() as db:
            # Get job details
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return {"status": "error", "message": "Job not found"}
            
            if not job.is_active:
                logger.info(f"Job {job_id} is inactive, skipping execution")
                return {"status": "skipped", "message": "Job is inactive"}
            
            # Create execution record
            execution = JobExecution(
                job_id=job_id,
                status="running"
            )
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            start_time = time.time()
            result = {"status": "success"}
            error_message = None
            
            try:
                # Get job handler
                handler = JobHandlerFactory.get_handler(job.job_type)
                if not handler:
                    raise ValueError(f"No handler found for job type: {job.job_type}")
                
                # Execute the job
                result = handler.execute(job.job_config or {})
                
                # Update job stats
                job.success_runs += 1
                job.last_run = datetime.now(timezone.utc)
                
                logger.info(f"Successfully executed job {job_id}")
                
            except Exception as e:
                result = {"status": "error", "message": str(e)}
                error_message = str(e)
                job.failed_runs += 1
                logger.error(f"Failed to execute job {job_id}: {e}")
            
            finally:
                # Calculate execution time
                execution_time = int((time.time() - start_time) * 1000)
                
                # Update execution record
                execution.completed_at = datetime.now(timezone.utc)
                execution.status = result["status"]
                execution.result = result
                execution.error_message = error_message
                execution.execution_time_ms = execution_time
                
                # Update job stats
                job.total_runs += 1
                job.updated_at = datetime.now(timezone.utc)
                
                # Calculate next run
                from app.services.scheduler_service import SchedulerService
                scheduler = SchedulerService()
                job.next_run = scheduler.calculate_next_run(
                    job.schedule_type, 
                    job.schedule_config
                )
                
                db.commit()
            
            return result
