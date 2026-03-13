from fastapi import APIRouter

from . import users
from .ml import router as ml_router

# from . import tickers, signals, logs, notifications, stats, system, watchlist

router = APIRouter(prefix="/admin", tags=["admin"])

router.include_router(users.router)
router.include_router(ml_router)
# router.include_router(signals.router)
# router.include_router(logs.router)
# router.include_router(notifications.router)
# router.include_router(stats.router)
# router.include_router(system.router)
# router.include_router(watchlist.router)
