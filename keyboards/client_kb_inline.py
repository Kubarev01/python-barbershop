from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    page: int = 1
    service_id: Optional[int] = None
    barber_id: Optional[int] = None
    date_time: Optional[str] = None





service_kb = InlineKeyboardBuilder()
services=['✂Записаться к мастеру','✉Связаться с нами','🔍Отследить мою запись']
for _ in services:
    service_kb.button(text=f"{_}", callback_data=f"service_{_}")

service_kb.adjust(1,1,1)




async def kb_service_choice(service_id):
    kb_service_choice = InlineKeyboardBuilder ()
    options = [ 'Выбрать' ]
    for _ in options:
        kb_service_choice.button (text=f"{_}", callback_data=f"service_choice_{_}_{service_id}")
    kb_service_choice.adjust(1)
    return kb_service_choice

async def kb_barber_choice(barber_id):
    kb_barber_choice = InlineKeyboardBuilder()
    options = [ 'Выбрать' ]
    for _ in options:
        kb_barber_choice.button (text=f"{_}", callback_data=f"barber_choice_{_}_{barber_id}")
    kb_barber_choice.adjust(1)
    return kb_barber_choice


###################################клавиатуры для многоуровневого меню#################################################

def get_user_main_btns(*,level:int,sizes:tuple[int]=(1,)):
    keyboard = InlineKeyboardBuilder()
    btns={
        '✍Записаться': 'time',
        '🛈О нас': "about"

    }
    for text,menu_name in btns.items():
        if menu_name == 'time':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+1,menu_name=menu_name).pack()))

        elif menu_name == 'about':
            keyboard.add (InlineKeyboardButton (text=text,
                                                callback_data=MenuCallBack (level=level,
                                                                            menu_name=menu_name).pack ()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_time_btns(*,level:int,sizes:tuple[int]=(1,)):
    keyboard = InlineKeyboardBuilder()
    #Здесь нужно подтянуть времена из апи гугл календаря
    btns={
        'ПН 16.00': 'service',
        '⬅Назад': 'back',

    }
    for text,menu_name in btns.items():
        if menu_name == 'service':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+1,menu_name=menu_name,date_time=text).pack()))

        elif menu_name == 'back':
            keyboard.add(InlineKeyboardButton(text=text,
                         callback_data=MenuCallBack(level=level-1,menu_name='main').pack()))


    return keyboard.adjust(*sizes).as_markup()

def get_user_service_btns(*,level:int,sizes:tuple[int]=(1,),services):
    keyboard = InlineKeyboardBuilder()
    #Здесь нужно подтянуть времена из апи гугл календаря
    btns={
        '⬅Назад':'back'
    }




    for service in services:
        keyboard.add (InlineKeyboardButton (text=service.name,

                                            callback_data=MenuCallBack (level=level + 1, menu_name=service.name,service_id=service.id).pack ()))

    for text, menu_name in btns.items():
        if menu_name == 'back':
            keyboard.add (InlineKeyboardButton (text=text,
                                        callback_data=MenuCallBack (level=level - 1, menu_name='time').pack()))
    return keyboard.adjust(*sizes).as_markup()



def get_services_btns(
        *,
        level:int,
        page:int,
        pagination_btns:dict,
        service_id:int,
        sizes: tuple[int] =(1,)
):
    keyboard=InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='⬅Назад',
                 callback_data=MenuCallBack(level=level-1,menu_name='time').pack()))
    #menu_name=add_service не является меню, а просто данные для создания тригера добавления услуги в заказ
    keyboard.add (InlineKeyboardButton (text='Выбрать',
                                        callback_data=MenuCallBack (level=level+1, menu_name='barbers',service_id=service_id).pack ()))
    keyboard.adjust(*sizes)

    #создание кнопок пагинации
    row=[]
    for text,menu_name in pagination_btns.items():
        if menu_name == 'next':
            row.append(InlineKeyboardButton (text=text,
                                            callback_data=MenuCallBack(level=level,
                                                                       menu_name=menu_name,
                                                                       page=page+1).pack()))
        elif menu_name =='previous':
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,
                                                                       menu_name=menu_name,
                                                                       page=page-1).pack()))
    return keyboard.row(*row).as_markup()



def get_barber_btns( *,
        level:int,
        page:int,
        pagination_btns:dict,
        barber_id:int,
        sizes: tuple[int] =(1,)
):
    keyboard=InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='⬅Назад',
                 callback_data=MenuCallBack(level=level-1,menu_name='time').pack()))
    #menu_name=add_barber не является меню, а просто данные для создания тригера добавления услуги в заказ
    keyboard.add (InlineKeyboardButton (text='Выбрать',
                                        callback_data=MenuCallBack (level=level+1, menu_name='add_barber',barber_id=barber_id).pack ()))
    keyboard.adjust(*sizes)

    #создание кнопок пагинации
    row=[]
    for text,menu_name in pagination_btns.items():
        if menu_name == 'next':
            row.append(InlineKeyboardButton (text=text,
                                            callback_data=MenuCallBack(level=level,
                                                                       menu_name=menu_name,
                                                                       page=page+1).pack()))
        elif menu_name =='previous':
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,
                                                                       menu_name=menu_name,
                                                                       page=page-1).pack()))
    return keyboard.row(*row).as_markup()