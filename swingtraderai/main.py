from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sqlalchemy as sa
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from swingtraderai.api.v1 import auth, tickers, users, watchlist
from swingtraderai.api.v1.admin import router as admin_router
from swingtraderai.core.config import settings
from swingtraderai.db.base import Base
from swingtraderai.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	try:
		async with engine.connect() as conn:
			await conn.execute(sa.text("SELECT 1"))
		print("Database connection successful")
	except Exception as e:
		print(f"Database connection failed: {e}")
		raise RuntimeError("Cannot connect to database") from e

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	yield

	await engine.dispose()


app = FastAPI(
	title="SwingTrader AI API",
	description="API для swing trading с анализом и уведомлениями",
	version="0.1.0",
	docs_url="/docs",
	redoc_url="/redoc",
	lifespan=lifespan,
)

if settings.CORS_ALLOWED_ORIGINS:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.CORS_ALLOWED_ORIGINS,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tickers.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")

app.include_router(admin_router, prefix="/api/v1")
