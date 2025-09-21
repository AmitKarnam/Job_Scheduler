from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum

class JobType(str, Enum):
    EMAIL_NOTIFICATION = "email_notification"
    DATA_PROCESSING = "data_processing"
class ScheduleType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"

class JobStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"

class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    job_type: JobType = Field(..., description="Type of job to execute")
    schedule_type: ScheduleType = Field(..., description="Scheduling method")
    schedule_config: Dict[str, Any] = Field(..., description="Schedule configuration")
    job_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Job-specific configuration")
    is_active: bool = Field(True, description="Whether the job is active")
    
    @validator('schedule_config')
    def validate_schedule_config(cls, v, values):
        schedule_type = values.get('schedule_type')
        if schedule_type == ScheduleType.CRON:
            if 'cron_expression' not in v:
                raise ValueError("cron_expression is required for cron schedule type")
        elif schedule_type == ScheduleType.INTERVAL:
            if 'interval_seconds' not in v:
                raise ValueError("interval_seconds is required for interval schedule type")
        return v

class JobUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    schedule_config: Optional[Dict[str, Any]] = None
    job_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class JobResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    job_type: str
    schedule_type: str
    schedule_config: Dict[str, Any]
    job_config: Optional[Dict[str, Any]]
    is_active: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    total_runs: int
    success_runs: int
    failed_runs: int
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    has_next: bool

class JobExecutionResponse(BaseModel):
    id: int
    job_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    
    class Config:
        from_attributes = True
