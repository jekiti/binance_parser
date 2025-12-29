
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from app.config import config
from app.nats.client import nats_publish
from app.schemas.ws_events import PriceEventType

router = APIRouter()

@router.post("/test/nats", tags=["test"])
async def test_nats_message(symbol: str = "BTCUSDT", price: float = 123.45):
    await nats_publish(
        config.NATS_SUBJECT,
        {
            "id": str(uuid4()),
            "symbol": symbol.strip().upper(),
            "price": price,
            "event_type": PriceEventType.ADD_DATA_FROM_REMOTE_SOURCE.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        },
    )
    return {"status": "ok"}
