from typing import Optional

from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Service, Barbers
from database.query import orm_get_banner, orm_get_items

from keyboards.client_kb_inline import get_user_main_btns, get_user_time_btns, get_user_service_btns, get_services_btns, \
    get_barber_btns

from utils_.paginator import Paginator


async def main_menu(
        session:AsyncSession,
        level:int,
        menu_name:str
):
    #получение изображения из бд
    banner =await orm_get_banner(session,menu_name)
    #Создание экземпляра для класса фотографий с описанием

    image=InputMediaPhoto(media=banner.image,caption=banner.description)

    #функция клавиатуры
    kbds = get_user_main_btns(level=level)

    return image,kbds



async def time_menu(
        session:AsyncSession,
        level:int,
        menu_name:str
):
    #получение изображения из бд
    banner =await orm_get_banner(session,menu_name)
    #Создание экземпляра для класса фотографий с описанием

    image=InputMediaPhoto(media=banner.image,caption=banner.description)

    #функция клавиатуры
    kbds = get_user_time_btns(level=level)

    return image,kbds


def pages(paginator:Paginator):
    btns= dict()
    if paginator.has_previous():
        btns['◀ Пред.']= 'previous'
    if paginator.has_next():
        btns['След. ▶'] = 'next'

    return btns



async def service_menu(
        session:AsyncSession,
        level:int,
        page:int
):
    services=await orm_get_items(session,Service)

    paginator=Paginator(services,page=page)
    service=paginator.get_page()[0]

    centered_text = f'{paginator.page}/{paginator.pages}'.center (65)

    image= InputMediaPhoto(
        media=service.image,
        caption=f'🚩<strong>{service.name}</strong>\
        \n{service.description}\n\n💸Стоимость: <i>{round(service.price,2)}</i>\
        \n\n<strong>{centered_text}</strong>',parse_mode='html'
    )

    paginator_btns=pages(paginator)

    kbds=get_services_btns(
        level=level,
        page=page,
        pagination_btns=paginator_btns,
        service_id=service.id
    )

    return  image,kbds




async def barber_menu(
        session: AsyncSession,
        level:int,
        page: int,

):
    barbers = await orm_get_items (session, Barbers)


    paginator = Paginator (barbers, page=page)
    barber = paginator.get_page () [ 0 ]


    centered_text = f'{paginator.page}/{paginator.pages}'.center (50)

    if barber.status is None:
        image = InputMediaPhoto (
            media=barber.photo,
            caption=f'<strong>{barber.name}</strong>\
                   \\n{barber.description}\
                   \n\n<strong>{centered_text}</strong>', parse_mode='html'
        )

    else: image = InputMediaPhoto (
        media=barber.photo,
        caption=f'<strong>{barber.name}</strong>\
           \n{barber.status.value}\n\n{barber.description}\
           \n<strong>{centered_text}</strong>', parse_mode='html'
    )

    paginator_btns = pages (paginator)

    kbds = get_barber_btns (
        level=level,
        page=page,
        pagination_btns=paginator_btns,
        barber_id=barber.id
    )

    return image, kbds







#функция получения клиентских изображений с описанием и клавиатур
async def get_client_content(
        session:AsyncSession,
        level: int,
        menu_name: str,
        page: Optional[int] = None,
        id_service: Optional[int] =  None,
        id_barber : Optional [int]=None
):

    if level == 0:
        return await main_menu(session,level,menu_name)
    if level == 1:
        return await time_menu(session,level,menu_name)
    if level == 2:
        return await service_menu(session,level,page)
    if level == 3:
        print(page)
        return await barber_menu(session,level,page)
