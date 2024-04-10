from aiogram import types, Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command, StateFilter

from aiogram.types import ContentType, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Service, Barbers
from database.query import orm_get_items, orm_get_single_item, orm_get_banner, orm_add_order
from handlers.customer_processing import get_client_content

from functions.send_sms import sending_sms
from functions.google_calendar import send_upcomming_events
from keyboards.client_kb_markup import send_contact
from keyboards.client_kb_inline import service_kb, kb_service_choice, kb_barber_choice, MenuCallBack

import asyncio

user = Router (name=__name__)

last_message_time = 0


class FsmClient (StatesGroup):
    phone_number = State ()
    send_phone_number = State ()
    verify_code = State ()
    get_name = State ()


@user.message (CommandStart ())
async def start_cmd (message: types.Message, session: AsyncSession):
    # await message.answer(f'Привет <u>{message.from_user.username}</u>!\n'
    #                                             f'Я специальный 🤖бот для записи в барбершоп <b>"SHARK"</b>\n'
    #                                             f'Я могу помочь тебе записаться на стрижку или связаться с администартором.\n\n'
    #                                             f'С чего начнем?',reply_markup=service_kb.as_markup(),parse_mode='html')
    media, reply_keyboard = await get_client_content (session, level=0, menu_name='main')
    await message.answer_photo (media.media, caption=media.caption, reply_markup=reply_keyboard)


@user.callback_query (MenuCallBack.filter ())
async def user_menu (callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession,
                     state: FSMContext):

    if callback_data.menu_name == 'service':
        await state.update_data (date_time=callback_data.date_time)

    if callback_data.menu_name == 'barbers':
        await state.update_data (id_service=callback_data.service_id)

    if callback_data.menu_name == 'add_barber':
        await state.update_data (id_barber=callback_data.barber_id)



        await state.set_state (FsmClient.phone_number)
        await get_number_from_user(callback,state,session)
        return

    media, reply_markup = await get_client_content (
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        id_service=callback_data.service_id,
        page=callback_data.page
    )

    await callback.message.edit_media (media=media, reply_markup=reply_markup)
    await callback.answer ()


#############################Продолжение регистрации пользователя с номером телефона#############################################

@user.callback_query(FsmClient.phone_number)
async def get_number_from_user (callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    banner = await orm_get_banner (session=session, page='main')
    image = InputMediaPhoto (media=banner.image, caption='Отлично! Осталось уточнить некоторые данные для записи')


    await callback_query.message.edit_media (media=image)

    await callback_query.message.answer (text='Напишите ваш номер в чат в формате +7*********'
                               'или нажмите на кнопкку', reply_markup=send_contact)
    await state.set_state (FsmClient.send_phone_number)


@user.message ((F.content_type == ContentType.CONTACT and FsmClient.send_phone_number),
               F.contact.phone_number.as_ ('phone_number'))
@user.message ((F.text.startswith == '+7' and F.text.len () == 12 and FsmClient.send_phone_number),
               F.text.phone_number.as_ ('phone_number'))
async def send_sms_code (message: types.Message, state: FSMContext, phone_number: str):
    # Проверяем, прошло ли уже 10 секунд с момента последней отправки сообщения

    await state.update_data(not_confirmed_number=phone_number)
    # global last_message_time
    # current_time = asyncio.get_event_loop ().time ()
    #
    # current_time = (int (str (round (current_time)) [ 2: ]))
    #
    #
    # if last_message_time != 0:
    #     await message.answer (
    #         f'Нельзя отправлять запрос смс так часто\nПодождите ещё {current_time - last_message_time} сек...')
    #     if current_time - last_message_time > 1:
    #         await asyncio.sleep (current_time - last_message_time)
    #
    # phone_number = str (phone_number)
    #
    # # фунция отправки sms-сообщения
    #
    # last_message_time = current_time

    sms_code = await sending_sms (f'Ваш код авторизации для барбершопа "Shark": ', receiver=phone_number)

    # прошел бесплатный пробный период и отправка смс больше не работает
    if sms_code:

        await state.update_data (code=sms_code)

        await message.answer ('🔒Введите код авторизации', reply_markup=types.ReplyKeyboardRemove ())
        await state.set_state (FsmClient.verify_code)

    else:
        await state.update_data (code=sms_code)
        await message.answer ('Что-то пошло не так, повторите попытку')
        await message.answer ('🔒Введите код авторизации', reply_markup=types.ReplyKeyboardRemove ())
        await state.set_state (FsmClient.verify_code)

    return


@user.message (F.text.as_ ('user_code'), FsmClient.verify_code)
async def verify_code (message: types.Message, state: FSMContext,session:AsyncSession ,user_code: str):
    data = await state.get_data ()
    code = str (data.get ('code'))
    print ("Код верификации:" + code)
    if user_code == code:
        await message.answer (f'🔓Ваш мобильный телефон успешно подтвержден!\nКак к вам можно обращаться?')
        await state.update_data(phone_number=data['not_confirmed_number'])
        await state.set_state (FsmClient.get_name)

    else:
        await message.answer ('Неверный код. Введите номер телефона заново',reply_markup=send_contact)
        await state.set_state(FsmClient.send_phone_number)


@user.message (F.text.as_ ('user_name'), FsmClient.get_name)
async def get_user_name (message: types.Message, state: FSMContext, user_name: str, session: AsyncSession):
    await state.update_data(name=user_name)

    data = await state.get_data ()




    await orm_add_order (
        session=session,
        data=data
    )

    banner = await orm_get_banner (session=session, page='main')
    barber=(await orm_get_single_item(session=session,item_id=data['id_barber'],table=Barbers)).name
    service = (await orm_get_single_item (session=session, item_id=data [ 'id_service' ], table=Service)).name


    mes = await message.answer (

        f'✅Отлично!\n<strong>{data [ "name" ].capitalize ()}</strong>, давайте подытожим:\n\n'
        f'📍Вы записаны на услугу: <u>"{service}"</u>\n'
        f'🧔🏻Ваш барбер: <u>{barber}</u>\n'
        f'📅Дата и время записи: <u>{data [ "date_time" ]}</u>\n\n'
        f'💬Просьба сообщать заранее в случае отмены записи! +79153451298', parse_mode='html')

    await state.clear()
    await mes.pin()
