
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.price import PriceRate
from app.database.session import get_async_session
from app.nats.nats_events import publish_price_event
from app.schemas.price import PriceRateCreate, PriceRateOut, PriceRateUpdate
from app.schemas.ws_events import PriceEventType

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/", response_model=list[PriceRateOut])
async def get_prices(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(PriceRate))
    return result.scalars().all()

@router.get("/{price_id}", response_model=PriceRateOut)
async def get_price(price_id: str, session: AsyncSession = Depends(get_async_session)):
    price = await session.get(PriceRate, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    return price

@router.post("/", response_model=PriceRateOut, status_code=status.HTTP_201_CREATED)
async def create_price(price_payload: PriceRateCreate, session: AsyncSession = Depends(get_async_session)):
    symbol = price_payload.symbol.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")

    exists = await session.execute(select(PriceRate).where(PriceRate.symbol == symbol))
    if exists.scalars().first() is not None:
        raise HTTPException(status_code=409, detail="Symbol already exists")

    price = PriceRate(
        symbol=symbol,
        price=price_payload.price,
        timestamp=datetime.now(timezone.utc),
    )
    session.add(price)
    await session.commit()
    await session.refresh(price)

    await publish_price_event(price, PriceEventType.CREATED)
    return price

@router.patch("/{price_id}", response_model=PriceRateOut)
async def update_price(price_id: str, price_payload: PriceRateUpdate, session: AsyncSession = Depends(get_async_session)):
    price = await session.get(PriceRate, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    price.price = price_payload.price
    price.timestamp = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(price)

    await publish_price_event(price, PriceEventType.UPDATED)
    return price

@router.delete("/{price_id}")
async def delete_price(price_id: str, session: AsyncSession = Depends(get_async_session)):
    price = await session.get(PriceRate, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    await session.delete(price)
    await session.commit()

    await publish_price_event(price, PriceEventType.DELETED)
    return {"status": "deleted"}
