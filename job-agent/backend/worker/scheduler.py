from celery.schedules import crontab
from backend.worker.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "poll-replies-daily": {
        "task": "tasks.poll_all_replies",
        "schedule": crontab(hour=8, minute=0),
    },
}
