
from sqlalchemy import select

from app.config import config
from app.database.models.base import Base
from app.database.session import async_session_factory, engine
from app.database.models.price import PriceRate 

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    defaults = [s.strip().upper() for s in config.DEFAULT_SYMBOLS.split(",") if s.strip()]
    if not defaults:
        return

    async with async_session_factory() as session:
        result = await session.execute(select(PriceRate.symbol))
        existing = set(result.scalars().all())

        created_any = False
        for sym in defaults:
            if sym in existing:
                continue
            session.add(PriceRate(symbol=sym, price=0))
            created_any = True

        if created_any:
            await session.commit()
