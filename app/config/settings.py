import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database credetials hardcoded for now, move to .env 
    database_url: str = os.getenv("DATABASE_URL", "mysql+pymysql://jobuser:jobpassword@localhost:3306/job_scheduler")
    
    # Redis credentials hardcoded for now, move to .env 
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Scheduler settings
    max_workers: int = 10
    job_default_max_instances: int = 3

    
    # API meta data
    api_title: str = "Job Scheduler Microservice"
    api_version: str = "1.0.0"
    api_description: str = "A scalable job scheduling service"
    
    
    class Config:
        env_file = ".env"

settings = Settings()
