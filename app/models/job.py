from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.models.base import Base

class Job(Base):
    __tablename__ = "jobs"
    
    # generic informations regarding job
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    job_type = Column(String(100), nullable=False)  
    
    # Scheduling
    schedule_type = Column(String(50), nullable=False)  # cron, interval
    schedule_config = Column(JSON, nullable=False)  # cron expression or interval config
    
    # Execution tracking
    is_active = Column(Boolean, default=True, nullable=False)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    # Job configuration
    job_config = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    
    # Execution stats
    total_runs = Column(Integer, default=0)
    success_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
