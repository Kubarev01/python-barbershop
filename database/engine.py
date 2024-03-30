import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base


#DB_URL='postgresql+asyncpg://postgres:Ui235GAj8883@localhost:5432/BarberShop'
#DB_URL='postgresql+asyncpg://Barber_shop:19022005@localhost:5432/BarberShop1'
engine = create_async_engine(DATABASE_URL)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        print("database has been created")
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        print("database has been dropped")
        await conn.run_sync(Base.metadata.drop_all)
