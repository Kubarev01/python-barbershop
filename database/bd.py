import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import DateTime, Float, String, Text, func,ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum
from typing import Optional



DB_URL='postgresql+asyncpg://postgres:Ui235GAj8883@localhost:5432/BarberShop'
engine = create_async_engine(DB_URL,echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class expirience(enum.Enum):
    an_expirenced='Барбер-мастер'
    begginer='Стажор'

class Time(enum.Enum):
    #сюда должно попадать время из гугл календаря
    pass



class Service(Base):
    __tablename__ = 'Service'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    image: Mapped[str] = mapped_column(String(150))

class Barbers(Base):
    __tablename__='Barbers'

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(100))
    status: Mapped[Optional[expirience]] = mapped_column(String(50))
    photo:Mapped[str] = mapped_column(String(100))
    description:Mapped[str] = mapped_column(Text)


class Orders(Base):
    __tablename__='Orders'

    id:Mapped[int] =mapped_column(primary_key=True,autoincrement=True)
    time:Mapped[str]
    Barber:Mapped[int]=mapped_column(ForeignKey('Barbers.id'))
    id_service:Mapped[int] = mapped_column(ForeignKey('Service.id'))


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

loop = asyncio.get_event_loop()
loop.run_until_complete(create_db())