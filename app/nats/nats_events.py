
from datetime import datetime, timezone

from app.config import config
from app.database.models.price import PriceRate
from app.nats.client import nats_publish
from app.schemas.ws_events import PriceEventType

async def publish_price_event(
    price: PriceRate,
    event_type: PriceEventType,
    source: str = "binance_price_watcher",
):
    event_data = {
        "id": str(price.id),
        "symbol": price.symbol,
        "price": float(price.price),
        "event_type": event_type.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
    }

    await nats_publish(config.NATS_SUBJECT, event_data)
