from abc import ABC, abstractmethod
from typing import Dict, Any
import random
import time
import logging

logger = logging.getLogger(__name__)

class JobHandler(ABC):
    """Abstract base class for job handlers"""
    
    @abstractmethod
    def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the job with given configuration"""
        pass

class EmailNotificationHandler(JobHandler):
    """Handler for email notification jobs"""
    
    def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sending email notifications"""
        recipients = config.get("recipients", ["user@example.com"])
        subject = config.get("subject", "Scheduled Notification")
        
        # Simulate email sending
        time.sleep(random.uniform(0.1, 0.5))
        
        logger.info(f"Sent email to {len(recipients)} recipients: {subject}")
        
        return {
            "status": "success",
            "recipients_count": len(recipients),
            "subject": subject,
            "sent_at": time.time()
        }

class DataProcessingHandler(JobHandler):
    """Handler for data processing jobs"""
    
    def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate data processing"""
        dataset = config.get("dataset", "default_dataset")
        operation = config.get("operation", "aggregate")
        
        # Simulate processing time
        time.sleep(random.uniform(0.2, 1.0))
        
        processed_records = random.randint(100, 10000)
        
        logger.info(f"Processed {processed_records} records from {dataset}")
        
        return {
            "status": "success",
            "dataset": dataset,
            "operation": operation,
            "processed_records": processed_records,
            "processing_time_ms": random.randint(200, 1000)
        }

# using factory pattern to decouple job type from handler implementation
class JobHandlerFactory:
    """Factory for creating job handlers"""
    
    _handlers = {
        "email_notification": EmailNotificationHandler(),
        "data_processing": DataProcessingHandler()
    }
    
    @classmethod
    def get_handler(cls, job_type: str) -> JobHandler:
        """Get handler for job type"""
        return cls._handlers.get(job_type)
    
    @classmethod
    def register_handler(cls, job_type: str, handler: JobHandler):
        """Register a new job handler"""
        cls._handlers[job_type] = handler
