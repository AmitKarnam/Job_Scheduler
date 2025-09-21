from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.models.base import Base
    
class JobExecution(Base):
    __tablename__ = "job_executions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, nullable=False, index=True)
    
    # Execution details
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    
    # Results
    result = Column(JSON, nullable=True)
    error_message = Column(LONGTEXT, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)