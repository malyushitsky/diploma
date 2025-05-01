from celery import Celery
from app import celery_globals

REDIS_URL = "redis://redis:6379/0"

celery = Celery(
    "arxiv_rag_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    task_send_sent_event=True,
    worker_send_task_events=True
)
celery.autodiscover_tasks(["app.tasks"])