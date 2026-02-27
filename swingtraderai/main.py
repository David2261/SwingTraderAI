from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from swingtraderai.db.base import Base
from swingtraderai.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield
	await engine.dispose()


app = FastAPI(lifespan=lifespan)
