from sqlalchemy import DateTime, Float, String, Text, func,ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from enum import Enum
from typing import Optional
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class expirience(Enum):
    an_expirenced='Барбер-мастер'
    begginer='Стажор'

class Time(Enum):
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
    status: Mapped[expirience or None] = mapped_column(String(50))
    photo:Mapped[str] = mapped_column(String(100))
    description:Mapped[str] = mapped_column(Text)


class Orders(Base):
    __tablename__='Orders'

    id:Mapped[int] =mapped_column(primary_key=True,autoincrement=True)
    time:Mapped[Time]
    Barber:Mapped[int]=mapped_column(ForeignKey('Barbers.id'))
    id_service:Mapped[int] = mapped_column(ForeignKey('Service.id'))

