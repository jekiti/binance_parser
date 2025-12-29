
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from app.schemas.price import PriceRateOut

class PriceEventType(str, Enum):
    CREATED = "price_created"
    UPDATED = "price_updated"
    DELETED = "price_deleted"
    COMPLETED = "task_completed"
    ADD_DATA_FROM_REMOTE_SOURCE = "add_data_from_remote_source"

class PriceEvent(BaseModel):
    event_type: PriceEventType
    price: PriceRateOut
    timestamp: datetime

    model_config = {"from_attributes": True}
