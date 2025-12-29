
import json
from datetime import datetime

from nats.aio.client import Client as NATS
from sqlalchemy import select

from app.config import config
from app.database.models.price import PriceRate
from app.database.session import async_session_factory
from app.schemas.price import PriceRateOut
from app.schemas.ws_events import PriceEvent, PriceEventType
from app.websocket.connection_manager import manager

nc = NATS()

async def nats_connect():
    if not nc.is_connected:
        await nc.connect(config.NATS_URL)
        await nc.subscribe(config.NATS_SUBJECT, cb=nats_handler)

async def nats_close():
    if nc.is_connected:
        await nc.close()

async def nats_publish(subject: str, data: dict):
    if not nc.is_connected:
        return
    await nc.publish(subject, json.dumps(data).encode())

async def nats_handler(msg):
    data: dict = json.loads(msg.data.decode())
    timestamp = datetime.fromisoformat(data["timestamp"])

    if data.get("source") != "binance_price_watcher":
        async with async_session_factory() as session:
            result = await session.execute(
                select(PriceRate).where(PriceRate.symbol == data["symbol"])
            )
            price = result.scalars().first()

            if price:
                price.price = data["price"]
                price.timestamp = timestamp
            else:
                price = PriceRate(
                    id=data["id"],
                    symbol=data["symbol"],
                    price=data["price"],
                    timestamp=timestamp,
                )
                session.add(price)

            await session.commit()

    event = PriceEvent(
        event_type=PriceEventType(data["event_type"]),
        price=PriceRateOut(
            id=data["id"],
            symbol=data["symbol"],
            price=data["price"],
            timestamp=timestamp,
        ),
        timestamp=timestamp,
    )

    await manager.broadcast(event)
