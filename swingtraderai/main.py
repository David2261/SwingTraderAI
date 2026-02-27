from fastapi import FastAPI
from swingtraderai.db.session import engine
from swingtraderai.db.base import Base
import swingtraderai.db.models

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
