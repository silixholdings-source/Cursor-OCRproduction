from celery import Celery
from .core.config import settings

# Create Celery instance
celery = Celery(
    "ai_erp_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.services.invoice_processor",
        "src.services.ocr",
        "src.services.workflow"
    ]
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery.autodiscover_tasks([
    "src.services"
])

if __name__ == "__main__":
    celery.start()
