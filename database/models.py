import datetime

from sqlalchemy import DateTime, Float, String, Text, func,ForeignKey,Enum as PgEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from enum import Enum
from typing import Optional, Annotated


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


intpk=Annotated[int,mapped_column(primary_key=True,autoincrement=True)]

class experience(Enum):
    an_experienced='🦈Барбер-мастер'
    beginner='🎓Стажор'




class Service(Base):
    __tablename__ = 'Service'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    image: Mapped[str] = mapped_column(String(150))


class Banner(Base):
    __tablename__ = 'Banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)



class Barbers(Base):
    __tablename__='Barbers'

    id:Mapped[intpk]
    name:Mapped[str] = mapped_column(String(100))
    status: Mapped[Optional[experience]]
    photo:Mapped[str] = mapped_column(String(100))
    description:Mapped[str] = mapped_column(Text)


class Orders(Base):
    __tablename__='Orders'

    id:Mapped[intpk]
    name:Mapped[str]=mapped_column(String(50))
    phone_number:Mapped[str]=mapped_column(String(12))
    id_barber:Mapped[int]=mapped_column(ForeignKey('Barbers.id'))
    date_time:Mapped[str]=mapped_column(nullable=True)
    id_service:Mapped[int] = mapped_column(ForeignKey('Service.id'))