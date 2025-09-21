from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/health", tags=["health"])

# basic health check endpoint
@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc),
            "database": "disconnected",
            "error": str(e)
        }
