import math

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Service, Barbers, experience, Banner, Orders


###################ЗАПРОСЫ ТОЛЬКО ДЛЯ ТАБЛИЦЫ БАРБЕРОВ########################

async def orm_add_barber(session:AsyncSession,data:dict):
    status = data.get ('status')

    if not status:

        obj = Barbers (
            name=data [ 'name' ],
            photo=data [ 'photo' ],
            description=data [ 'description' ]
        )
    else:

        if status==experience.an_experienced:
            status='an_experienced'
        elif status==experience.beginner:
            status='beginner'
        obj = Barbers (
            name=data [ 'name' ],
            photo=data [ 'photo' ],
            status=status,
            description=data [ 'description' ]
        )
    session.add (obj)
    await session.commit ()



async def orm_update_barber(session: AsyncSession, barber_id: int, data:dict):
    status = data.get ('status')


    if 'status' in data:
        status_='eror'
        if status == experience.an_experienced:

            status_ = 'an_experienced'

        elif status == experience.beginner:

            status_='beginner'
        query = update(Barbers).where(Barbers.id == barber_id).values(
        name=data["name"],
        status=status,
        description=data["description"],
        photo=data["photo"])
    else:
        query = update (Barbers).where (Barbers.id == barber_id).values (
            name=data [ "name" ],
            description=data [ "description" ],
            photo=data [ "photo" ])


    await session.execute(query)
    await session.commit()

#####################ЗАПРОСЫ ТОЛЬКО ДЛЯ ТАБЛИЦЫ БАНЕРОВ##############


async def orm_add_banner_description(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


###################ЗАПРОСЫ ТОЛЬКО ДЛЯ ТАБЛИЦЫ УСЛУГ########################
async def orm_add_service(session:AsyncSession,data:dict):
    obj = Service(
        name=data [ 'name' ],
        description=data [ 'description' ],
        image=data [ 'image' ],
        price=float (data [ 'price' ])

    )
    session.add (obj)
    await session.commit ()

async def orm_update_service(session: AsyncSession, product_id: int, data:dict):
    query = update(Service).where(Service.id == product_id).values(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],)
    await session.execute(query)
    await session.commit()



########################Общие запросы##################################
async def orm_get_items(session: AsyncSession,table):
    query = select(table)
    result = await session.execute(query)

    return result.scalars().all()


async def orm_get_single_item(session: AsyncSession, item_id: int,table):
    query = select(table).where(table.id == item_id)
    result = await session.execute(query)
    return result.scalar()



async def orm_delete_item(session: AsyncSession, item_id: int,table):
    query = delete(table).where(table.id == item_id)
    await session.execute(query)
    await session.commit()

#############################Запросы для таблицы заказов##############################

async def orm_add_order(session:AsyncSession,data:dict):
    obj = Orders (
        name=data ['name'],
        phone_number=data [ 'phone_number' ],
        id_barber=data[ 'id_barber' ],
        date_time=data[ 'date_time' ],
        id_service= data['id_service']

    )
    session.add (obj)
    await session.commit ()