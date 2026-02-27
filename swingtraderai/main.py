from fastapi import FastAPI

from swingtraderai.db.base import Base
from swingtraderai.db.session import engine

app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
