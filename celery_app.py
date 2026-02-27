from celery import Celery
from swingtraderai.core.config import DATABASE_URL, REDIS_URL

celery = Celery(
	"swingtraderai",
	broker=REDIS_URL,
	backend=REDIS_URL,
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