
import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
backend_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

celery_app = Celery("doctorvit", broker=broker_url, backend=backend_url)
celery_app.conf.update(
    task_routes={
        "tasks.run_notebook_task": {"queue": "gpu"},
        "tasks.predict_task": {"queue": "gpu"},
    },
    worker_concurrency=1,  # one GPU job per worker by default
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
