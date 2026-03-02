from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from swingtraderai.api.v1 import auth, tickers, users, watchlist
from swingtraderai.db.base import Base
from swingtraderai.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield
	await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tickers.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
