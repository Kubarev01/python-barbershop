from aiogram import types,Router,F
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart,Command

from aiogram.types import ContentType
from keyboards.calendar_inline import get_inline_calendar
from functions.send_sms import sending_sms
from functions.google_calendar import send_upcomming_events
from keyboards.client_kb_markup import send_contact
from keyboards.client_kb_inline import service_kb



import asyncio


user = Router(name=__name__)


class FsmClient(StatesGroup):
    write_down=State()

    phone_number=State()
    send_phone_number=State()
    get_code=State()
    code=State()
    verify_code=State()
    choose_time=State()


@user.message(CommandStart())
async def start_cmd(message:types.Message):
    await message.answer(f'Привет <u>{message.from_user.username}</u>!\n'
                                                f'Я специальный 🤖бот для записи в барбершоп <b>"SHARK"</b>\n'
                                                f'Я могу помочь тебе записаться на стрижку или связаться с администартором.\n\n'
                                                f'С чего начнем?',reply_markup=service_kb.as_markup(),parse_mode='html')
    await send_upcomming_events()


@user.callback_query(F.data=='service_✂Записаться к мастеру')
async def service(callback_query:types.CallbackQuery,state:FSMContext):
    print('запись')
    await callback_query.message.edit_text('Выберите услугу:',reply_markup=None,parse_mode='html')
    await state.set_state(FsmClient.phone_number)






@user.message(FsmClient.phone_number)
async def get_number_from_user(message:types.Message,state:FSMContext):
    await message.answer(text='Напишите ваш номер в чат в формате +7*********'
                                'или нажмите на кнопкку',reply_markup=send_contact)
    await state.set_state(FsmClient.send_phone_number)

@user.message((F.content_type==ContentType.CONTACT and FsmClient.send_phone_number),F.contact.phone_number.as_('phone_number'))
@user.message((F.text.startswith=='+7' and  F.text.len()==12 and FsmClient.send_phone_number),F.text.phone_number.as_('phone_number'))
@user.message(Command('phone'))
async def send_sms_code(message:types.Message,state:FSMContext,phone_number:str):
    phone_number=str(phone_number)
    print('номер: '+phone_number)
    # фунция отправки sms-сообщения
    sms_code=await sending_sms(f'Ваш код авторизации: ',receiver=phone_number)
    # прошел бесплатный пробный период и отправка смс больше не работает
    if sms_code:

        await state.update_data(code=sms_code)

        await message.answer ('Введите код авторизации', reply_markup=None)
        await state.set_state (FsmClient.verify_code)

    else:
        await state.update_data (code=sms_code)
        await message.answer ('Что-то пошло не так, повторите попытку позже')
        await message.answer ('Введите код авторизации', reply_markup=None)
        await state.set_state (FsmClient.verify_code)
    #мидлварь
    #ограничение на отправку сообщений
    await asyncio.sleep(30)
    return




@user.message(F.text.as_('user_code'))
async def verify_code(message:types.Message,state:FSMContext,user_code:str):
    data = await state.get_data()
    code = str(data.get('code'))
    print("Код верификации:"+code)
    if user_code==code:
        await message.answer('Ваш мобильный телефон успешно подтвержден!')
        await state.set_state(FsmClient.choose_time)

    else:
        await message.answer('Неверный код. Пройдите процесс верификации заново')
        await get_number_from_user(message,state)


@user.message(FsmClient.choose_time)
async def choose_time(message:types.Message,state:FSMContext):
    pass

    #await bot.send_message(message.from_user.id,'Выберите дату',reply_markup=)


