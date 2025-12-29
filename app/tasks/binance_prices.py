
import asyncio
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database.models.price import PriceRate
from app.database.session import async_session_factory
from app.nats.nats_events import publish_price_event
from app.schemas.ws_events import PriceEventType

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"

async def fetch_binance_price(symbol: str) -> float:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            BINANCE_TICKER_URL,
            params={"symbol": symbol},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return float(data["price"])

async def generate_binance_prices(session: AsyncSession):
    result = await session.execute(select(PriceRate))
    prices = result.scalars().all()

    for item in prices:
        try:
            new_price = await fetch_binance_price(item.symbol)
        except Exception:
            continue

        if float(item.price) != float(new_price):
            item.price = new_price
            item.timestamp = datetime.now(timezone.utc)
            await publish_price_event(item, PriceEventType.UPDATED)

async def run_binance_update():
    async with async_session_factory() as session:
        async with session.begin():
            await generate_binance_prices(session)

async def periodic_task():
    try:
        while True:
            try:
                await run_binance_update()
            except Exception:
                pass
            await asyncio.sleep(config.FETCH_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        pass
