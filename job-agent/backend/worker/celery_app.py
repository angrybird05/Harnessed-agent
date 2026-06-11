from celery import Celery
from backend.config import settings

celery_app = Celery(
    "job_agent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Import tasks so they are registered
celery_app.autodiscover_tasks(["backend.worker"])

# Import scheduler to register beat schedule in ALL processes (worker, beat, api)
import backend.worker.scheduler  # noqa: F401, E402

