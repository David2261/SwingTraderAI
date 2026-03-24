from typing import Any, List

import redis.asyncio as redis

from swingtraderai.config import REDIS_URL


async def rotate_api_metrics() -> None:
	"""
	Ротация метрик API: сохраняет данные за предыдущий период и обнуляет счетчики.
	"""
	r: redis.Redis[Any] = redis.Redis.from_url(REDIS_URL)
	pipe = r.pipeline()

	total_requests = await r.get("metrics:api:total_requests")
	total_requests_value: int = int(total_requests) if total_requests is not None else 0

	rate_limit_hits = await r.get("metrics:api:rate_limit_hits")
	rate_limit_value: int = int(rate_limit_hits) if rate_limit_hits is not None else 0

	pipe.set("metrics:api:total_requests:yesterday", total_requests_value)
	pipe.set("metrics:api:rate_limit_hits:yesterday", rate_limit_value)

	pipe.set("metrics:api:total_requests", 0)
	pipe.set("metrics:api:rate_limit_hits", 0)

	endpoints: List[str] = ["/predict", "/train", "/health", "/metrics"]
	for ep in endpoints:
		pipe.set(f"metrics:api:endpoint:{ep}:requests", 0)
		pipe.set(f"metrics:api:endpoint:{ep}:errors", 0)

	await pipe.execute()
