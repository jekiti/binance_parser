
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base

class PriceRate(Base):
    __tablename__ = "price_rates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    price: Mapped[float] = mapped_column(Numeric(20, 10))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
