# Job Scheduler Microservice

A scalable, production-ready job scheduling microservice built with FastAPI, SQLAlchemy, MySQL, Redis, and APScheduler.

---

## Features
- **Job Scheduling:** Supports cron and interval-based jobs.
- **Job Types:** Extensible for data processing and email notification jobs.
- **Persistence:** Jobs and execution logs stored in MySQL; schedules persisted in Redis.
- **REST API:** Create, update, delete, and query jobs via HTTP endpoints.
- **Robustness:** Survives restarts, supports distributed scheduling, and provides safe DB session management.
- **Extensible:** Easily add new job types and handlers.

---

## Architecture
- **FastAPI**: REST API layer
- **SQLAlchemy**: ORM for MySQL
- **Alembic**: Database migrations
- **APScheduler**: Job scheduling and execution
- **Redis**: Persistent job store for APScheduler
- **Docker Compose**: For local MySQL and Redis services

---

## Getting Started

### 1. Clone the Repository
```sh
git clone https://github.com/AmitKarnam/Job_Scheduler
cd Job_Scheduler
```

### 2. Set Up Python Environment
```sh
python -m venv venv
./venv/Scripts/activate  # On Windows
source venv/bin/activate  # On Linux
pip install -r requirements.txt
```

### 3. Start MySQL and Redis (Docker Compose)
```sh
docker-compose up -d
```

### 4. Configure Environment Variables
Edit `.env` or `app/config/settings.py` as needed for DB and Redis URLs.

### 5. Run Database Migrations
```sh
alembic upgrade head
```

### 6. Start the Application
```sh
uvicorn main:app --reload
```

---

## API Usage

### Create a Job (POST /api/v1/jobs/)
```json
{
  "name": "Test Job",
  "description": "A test job for the scheduler",
  "job_type": "data_processing",
  "schedule_type": "interval",
  "schedule_config": { "interval_seconds": 60 },
  "job_config": { "script": "print('Hello!')" }
}
```
