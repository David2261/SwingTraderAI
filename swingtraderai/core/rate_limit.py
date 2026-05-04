from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from swingtraderai.core.config import settings


async def _rate_limit_exceeded_handler(
	request: Request, exc: RateLimitExceeded
) -> JSONResponse:
	"""Красивая обработка превышения лимита"""
	return JSONResponse(
		status_code=status.HTTP_429_TOO_MANY_REQUESTS,
		content={
			"detail": "Слишком много запросов. Попробуйте позже.",
			"type": "rate_limit_exceeded",
			"limit": str(exc.detail),
		},
	)


def get_rate_limit_key(request: Request) -> str:
	"""Приоритет: User ID → IP"""
	if (
		hasattr(request.state, "user")
		and request.state.user
		and getattr(request.state.user, "id", None)
	):
		return f"user:{request.state.user.id}"

	return f"ip:{get_remote_address(request)}"


limiter = Limiter(
	key_func=get_rate_limit_key,
	default_limits=["120/minute"],
	storage_uri=settings.REDIS_URL,
	strategy="fixed-window",
)
