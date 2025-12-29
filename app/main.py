
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import background_task_endpoints, price_endpoints, websocket_endpoints, nats_test
from app.database.init_db import init_db
from app.nats.client import nats_close, nats_connect
from app.tasks.binance_prices import periodic_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_task())
    try:
        await init_db()
        await nats_connect()
        yield
    finally:
        task.cancel()
        await nats_close()

app = FastAPI(lifespan=lifespan)

app.include_router(price_endpoints.router)
app.include_router(websocket_endpoints.router)
app.include_router(background_task_endpoints.router)
app.include_router(nats_test.router)
