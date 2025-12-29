
from datetime import datetime
from pydantic import BaseModel

class PriceRateCreate(BaseModel):
    symbol: str
    price: float

class PriceRateUpdate(BaseModel):
    price: float

class PriceRateOut(BaseModel):
    id: str
    symbol: str
    price: float
    timestamp: datetime

    model_config = {"from_attributes": True}
