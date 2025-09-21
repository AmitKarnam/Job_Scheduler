from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import  ThreadPoolExecutor
from croniter import croniter
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from app.models.job import Job
from app. config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing job scheduling using APScheduler"""
    
    def __init__(self):
        # Configure job stores
        jobstores = {
            'default': RedisJobStore(host='localhost', port=6379, db=1)
        }
        
        # Configure executors
        executors = {
            'default': ThreadPoolExecutor(max_workers=settings.max_workers)
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")
    
    def calculate_next_run(self, schedule_type: str, schedule_config: Dict[str, Any]) -> datetime:
        """Calculate the next run time for a job"""
        now = datetime.now(timezone.utc)
        
        if schedule_type == "cron":
            cron_expression = schedule_config.get("cron_expression")
            if not cron_expression:
                raise ValueError("cron_expression is required for cron schedule")
            
            cron = croniter(cron_expression, now)
            return cron.get_next(datetime)
        
        elif schedule_type == "interval":
            interval_seconds = schedule_config.get("interval_seconds")
            if not interval_seconds:
                raise ValueError("interval_seconds is required for interval schedule")
            
            return now + timedelta(seconds=interval_seconds)
        
        else:
            raise ValueError(f"Unsupported schedule type: {schedule_type}")
    
    def schedule_job(self, job: Job):
        """Schedule a job for execution"""
        from app.services.job_executor import JobExecutor
        
        job_id = f"job_{job.id}"
        
        if job.schedule_type == "cron":
            self.scheduler.add_job(
                JobExecutor.execute_job,
                'cron',
                id=job_id,
                args=[job.id],
                **self._parse_cron_config(job.schedule_config["cron_expression"]),
                replace_existing=True
            )
        
        elif job.schedule_type == "interval":
            self.scheduler.add_job(
                JobExecutor.execute_job,
                'interval',
                id=job_id,
                args=[job.id],
                seconds=job.schedule_config["interval_seconds"],
                replace_existing=True
            )
        
        logger.info(f"Scheduled job {job.id}: {job.name}")
    
    def unschedule_job(self, job_id: int):
        """Remove a job from the scheduler"""
        scheduler_job_id = f"job_{job_id}"
        try:
            self.scheduler.remove_job(scheduler_job_id)
            logger.info(f"Unscheduled job {job_id}")
        except Exception as e:
            logger.warning(f"Job {job_id} was not in scheduler: {e}")
    
    def reschedule_job(self, job: Job):
        """Reschedule an existing job"""
        self.unschedule_job(job.id)
        if job.is_active:
            self.schedule_job(job)
    
    def _parse_cron_config(self, cron_expression: str) -> Dict[str, Any]:
        """Parse cron expression into APScheduler format"""
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts")
        
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'day_of_week': parts[4]
        }
