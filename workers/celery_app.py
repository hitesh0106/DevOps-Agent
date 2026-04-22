"""
DevOps Agent — Celery Application Configuration
"""

from celery import Celery
from config.settings import settings

celery_app = Celery(
    "devops_agent",
    broker=settings.redis.redis_url,
    backend=settings.redis.redis_url,
    include=[
        "workers.agent_worker",
        "workers.pipeline_worker",
        "workers.monitoring_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=280,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_routes={
        "workers.agent_worker.*": {"queue": "agent"},
        "workers.pipeline_worker.*": {"queue": "pipeline"},
        "workers.monitoring_worker.*": {"queue": "monitoring"},
    },
)

celery_app.conf.beat_schedule = {
    "health-check-every-5-min": {
        "task": "workers.monitoring_worker.periodic_health_check",
        "schedule": 300.0,
    },
}
