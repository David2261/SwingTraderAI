from celery import Celery

from swingtraderai.core.config import settings

celery = Celery(
	"swingtraderai",
	broker=settings.REDIS_URL,
	backend=settings.REDIS_URL,
	include=[
		"swingtraderai.tasks",
	],
)

celery.conf.update(
	task_serializer="json",
	accept_content=["json"],
	result_serializer="json",
	timezone="UTC",
	enable_utc=True,
)
