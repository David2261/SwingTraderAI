import time
from typing import Any

import redis.asyncio as redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from swingtraderai.core.exceptions import InvalidAPIMetricsException


class APIMetricsMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: Any, redis_client: redis.Redis) -> None:
		super().__init__(app)
		self.redis = redis_client

	async def dispatch(self, request: Request, call_next: Any) -> Any:
		start_time = time.perf_counter()

		path = request.url.path
		if path.startswith("/api/v1/admin/ml/predict/"):
			endpoint = "/predict"
		elif path.startswith("/api/v1/admin/ml/train/"):
			endpoint = "/train"
		else:
			endpoint = path.rstrip("/")

		response = None
		status_code = 500
		is_error = False
		is_rate_limit = False

		try:
			response = await call_next(request)
			status_code = response.status_code
		except Exception:
			is_error = True
			raise
		finally:
			process_time = time.perf_counter() - start_time

			if status_code >= 400:
				is_error = True
			if status_code == 429:
				is_rate_limit = True

			try:
				pipe = self.redis.pipeline()
				await pipe.incr("metrics:api:total_requests")
				await pipe.incr(f"metrics:api:endpoint:{endpoint}:requests")

				if is_error:
					await pipe.incr(f"metrics:api:endpoint:{endpoint}:errors")
				if is_rate_limit:
					await pipe.incr("metrics:api:rate_limit_hits")

				await pipe.execute()
			except Exception as e:
				InvalidAPIMetricsException(detail=str(e))

			if response:
				response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

		return response
