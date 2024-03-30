from aiogram import types,Router,F
from aiogram.filters import Command, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup,State
from sqlalchemy.ext.asyncio import AsyncSession


from database.models import Service, Barbers, experience
from database.query import orm_add_service, orm_get_items, orm_add_barber, orm_get_single_item, orm_update_service, \
    orm_delete_item, orm_update_barber, orm_get_info_pages, orm_change_banner_image
from filters.chat_type import ChatTypeFilter, isAdmin
from keyboards.admin_inline_kb import Admin_kb, ADD_OR_EDIT_kb, ADD_OR_EDIT_Barbers_kb, choose_barber_status_kb, \
    barber_param_to_change, service_param_to_change, statuses
from keyboards.client_kb_inline import kb_barber_choice, kb_service_choice


admin_router= Router(name='admin')
admin_router.message.filter(ChatTypeFilter(["private"]),isAdmin())


@admin_router.message(Command("admin"))
async def admin_check(message:types.Message):
    await message.answer('Добро пожаловать в режим администратора!',reply_markup=Admin_kb.as_markup())




@admin_router.callback_query(F.data=='admin_Просмотр услуг')
async def edit_service(callback_query:types.CallbackQuery,session:AsyncSession):
    for service in await orm_get_items(session,table=Service):
        await callback_query.message.answer_photo(service.image,
                                                  caption=f'<strong>{service.name}\n'
                                                          f'</strong>\n{service.description}\n'
                                                          f'Стоимость: {round(service.price,2)}',parse_mode='html')







######################### для добавления услуг админом ###################

class AddService(StatesGroup):
    add_name=State()
    add_description=State()
    add_photo = State ()
    add_price=State()


    alerts = {
    'AddService:add_name':'Введите имя заново:',
    'AddService:add_description':'Введите описание заново:',
    'AddService:add_photo':'Отправьте фото заново',
    'AddService:add_price':'Введите цену заново'


    }

class EditService(StatesGroup):
    start_edit=State()
    choice_what_to_edit=State()
    edit=State()





@admin_router.callback_query(F.data=='admin_Услуги')
async def edit_service(callback_query:types.CallbackQuery):
    await callback_query.message.edit_text('Нужно добавить или редактировать?',reply_markup=ADD_OR_EDIT_kb.as_markup())


@admin_router.callback_query(StateFilter(None),F.data.startswith('add_or_edit_'))
async def add_service_start(callback_query:types.CallbackQuery,state:FSMContext,session:AsyncSession):
    if callback_query.data.split('_')[-1] =='Добавить':
        await callback_query.message.edit_text(text=
                                            f'Добавление  новой услуги\nДля начала введите название\n\n'
                                           f'Напишите "/назад" для возвращения к предыдущему шагу"\n'
                                           f'"/отмена" для возврата в главное меню')
        await state.set_state(AddService.add_name)
    if callback_query.data.split('_')[-1] =='Редактировать':
        await callback_query.message.edit_text(text=
                                            f'Редактирование услуги\nВыберите услугу для редактирования\n\n'
                                           f'Напишите "/назад" для возвращения к предыдущему шагу"\n'
                                           f'"/отмена" для возврата в главное меню')

        for service in await orm_get_items(session=session, table=Service):
            await callback_query.message.answer_photo (service.image,
                                                       caption=f'<strong>{service.name}\n'
                                                               f'</strong>\n{service.description}\n'
                                                               f'Стоимость: {round (service.price, 2)}',
                                                       parse_mode='html', reply_markup=(
                    await kb_service_choice (service_id=service.id)).as_markup ())

        await state.set_state(EditService.start_edit)


    if callback_query.data.split ('_') [ -1 ] == 'Вернуться назад':
        await state.clear ()
        await callback_query.message.edit_text (text='Админ-панель', reply_markup=Admin_kb.as_markup())



@admin_router.message(StateFilter('*'),Command('отмена'))
@admin_router.message(StateFilter('*'),F.text.casefold() == "отмена")
async def cancel_handler(message:types.Message,state:FSMContext):
    curent_state=await state.get_state()
    if curent_state is None:
        return

    await state.clear ()
    await message.answer("Действия отменены",reply_markup=Admin_kb.as_markup())


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddService.add_name:
        await message.answer(
            'Предыдущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AddService.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddService.alerts[previous.state]}"
            )
            return
        previous = step

############################Хендлеры редактирования услуги###################

@admin_router.callback_query(EditService.start_edit,F.data.startswith('service_choice_'))
async def start_editing_service(callback_query:types.CallbackQuery,state:FSMContext):

    await state.update_data(service_id=callback_query.data.split('_')[-1])

    await callback_query.message.edit_reply_markup(reply_markup=(await service_param_to_change()).as_markup())
    #await callback_query.message.edit_text('Что нужно изменить в услуге?',reply_markup=(await service_param_to_change()).as_markup())
    await state.set_state(EditService.choice_what_to_edit)

@admin_router.callback_query(EditService.choice_what_to_edit,F.data.startswith('service_param_edit_'))
async def start_editing_service(callback_query:types.CallbackQuery,state:FSMContext,session:AsyncSession):
        if callback_query.data.split('_')[-1] == 'Назад':
            data = await state.get_data ()
            await callback_query.message.edit_reply_markup (
                reply_markup=(await kb_service_choice(data['service_id'])).as_markup ())
            await state.set_state(EditService.start_edit)
            return
        if callback_query.data.split('_')[-1] =='Удалить':
            data=await state.get_data()
            await orm_delete_item(session=session,item_id=data['service_id'],table=Service)
            await callback_query.message.edit_text('Услуга удалена!',reply_markup=Admin_kb.as_markup())
            await state.clear()
            return
        if not callback_query.data.split('_')[-1] == 'Цена':
            await callback_query.message.answer(f'Введите новое {callback_query.data.split("_")[-1].lower()}',reply_markup=None)
        else:
            await callback_query.message.answer(f'Введите новую {callback_query.data.split ("_") [ -1 ].lower ()}',
                                                    reply_markup=None)
        await state.update_data (what_to_edit=callback_query.data.split('_')[-1])
        await state.set_state(EditService.edit)


@admin_router.message (F.text.as_ ('new_service_param') | F.photo[-1].file_id.as_('new_service_param'), EditService.edit)
async def edit_name_service (message: types.CallbackQuery, state: FSMContext, session: AsyncSession,
                             new_service_param: str):

    service = await state.get_data ()
    service_id = service [ 'service_id' ]
    data = await orm_get_single_item (item_id=service_id, table=Service, session=session)
    param = service [ 'what_to_edit' ]
    old_param = ''

    if param == 'Название':
        old_param = data.name
        data.name = new_service_param
        service['name']=new_service_param
        service['description']=data.description
        service['price']=data.price
        service['image']=data.image

    elif param == 'Описание':
        old_param = data.description
        data.description = new_service_param
        service [ 'name' ] = data.name
        service['description']=new_service_param
        service [ 'price' ] = data.price
        service [ 'image' ] = data.image

    elif param == 'Фото':
        old_param = data.image
        data.image = new_service_param
        service [ 'name' ] = data.name
        service [ 'description' ] = data.description
        service [ 'price' ] = data.price
        service['image']=new_service_param

    elif param == 'Цена':
        old_param = data.price
        data.price = new_service_param
        service [ 'name' ] = data.name
        service [ 'description' ] = data.description
        service['price']=new_service_param
        service [ 'image' ] = data.image




    await orm_update_service (data=service, product_id=service_id, session=session)
    await state.clear()
    await message.answer (f'{old_param} --> {new_service_param}', reply_markup=Admin_kb.as_markup())



##########################хендлеры добавления услуги#########################

@admin_router.message(F.text.as_('service_name'),AddService.add_name)
async def add_service_name(message:types.Message,state:FSMContext,service_name:str):
    #добавление имени в бд

        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
    if 4 >= len (message.text) >= 150:
        await message.answer (
                "Название услуги не должно превышать 150 символов\nили быть менее 5ти символов.\nВведите заново"
        )
        return

    await state.update_data (name=service_name)

    await message.answer (f'Введите описание')
    await state.set_state (AddService.add_description)

@admin_router.message(AddService.add_name)
async def add_service_name1(message:types.Message,state:FSMContext,service_name:str):
    await message.answer (f'Вы ввели недопустимые данные, введите текст названия услуги')





@admin_router.message (F.text.as_('service_description'), AddService.add_description)
async def add_service_description(message: types.Message, state: FSMContext, service_description: str):

    await state.update_data (description=service_description)
    await message.answer (f'Пришлите фото')
    await state.set_state (AddService.add_photo)


@admin_router.message (AddService.add_description)
async def add_service_description1(message: types.Message, state: FSMContext, service_description: str):
    await message.answer (f'Вы ввели недопустимые данные, введите текст описания услуги')


@admin_router.message (F.photo, AddService.add_photo)
async def add_service_photo (message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer (f'Введите цену цифрами')
    await state.set_state (AddService.add_price)

@admin_router.message ( AddService.add_photo)
async def add_service_photo1 (message: types.Message, state: FSMContext):
    await message.answer (f'Вы ввели недопустимые данные, отправьте фотографию услуги')




@admin_router.message (F.text.as_('service_price'), AddService.add_price)
async def add_service_price (message: types.Message, state: FSMContext, service_price:str,session:AsyncSession):
    await state.update_data (price=service_price)
    data=await state.get_data()
    #await message.answer_photo(f'имя:{data["name"]}\n{data["photo"]}\n{data["description"]}\n{data["price"]} руб.')
    try:
        await orm_add_service(session,data)
        await message.answer("Товар добавлен",reply_markup=Admin_kb.as_markup())
        await state.clear()

    except Exception as e:
        if type(service_price) is float:
            await message.answer(
            f"Ошибка: \n{str(e)}\nОбратитесь к разработчику за решением проблемы",reply_markup=Admin_kb.as_markup())
            await state.clear ()
        else:
            await message.answer (f'Вы ввели недопустимые данные, отправьте цену услуги цифрами')


@admin_router.message (AddService.add_price)
async def add_service_price (message: types.Message, state: FSMContext, service_price:str):
    await message.answer (f'Вы ввели недопустимые данные, отправьте цену услуги цифрами')


################# Микро FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.callback_query(StateFilter(None), F.data == 'admin_Банеры')
async def add_image2(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    print('добавление банера')
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await callback_query.message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")









######################### FSM для добавления/изменения барберов админом ###################


class AddBarber(StatesGroup):
    add_name=State()
    add_status=State()
    add_photo=State()
    add_descriprtion=State()

    alerts = {
        'AddBarber:add_name': 'Введите имя заново:',
        'AddBarber:add_status': 'Выберите статус заново:',
        'AddBarber:add_photo': 'Отправьте фото заново',
        'AddBarber:add_description': 'Введите описание заново'

    }

class EditBarber(StatesGroup):
    start_edit = State ()
    choice_what_to_edit = State ()
    edit = State ()


@admin_router.callback_query(F.data=='admin_Мастера')
async def edit_barber(callback_query:types.CallbackQuery):
    await callback_query.message.edit_text(text='Нужно добавить или редактировать мастера?',reply_markup=ADD_OR_EDIT_Barbers_kb.as_markup())


@admin_router.callback_query(StateFilter(None),F.data.startswith('add_barbers_or_edit_'))
async def add_barber_start(callback_query:types.CallbackQuery,state:FSMContext,session:AsyncSession):
    if callback_query.data.split('_')[-1] == 'Добавить':
        await callback_query.message.edit_text(f'Добавление нового барбера\nДля начала введите Имя\n\n'
                                           f'Напишите "/назад" для возвращения к предыдущему шагу"\n'
                                           f'"/отмена" для возврата в главное меню')
        await state.set_state(AddBarber.add_name)
    if callback_query.data.split('_')[-1] == 'Редактировать':
        for barber in await orm_get_items (session, table=Barbers):

            #замена полей на их значения для вывода status из enum класса
            status=''
            if barber.status:
                if barber.status==experience.an_experienced:
                    status=experience.an_experienced.value
                elif barber.status==experience.beginner:
                    status=experience.beginner.value

            await callback_query.message.answer_photo (barber.photo,
                                                       caption=f'<strong>{barber.name}\n'
                                                               f'</strong>\n<i>{status}</i>\n'
                                                               f'{barber.description}',
                                                       parse_mode='html', reply_markup=(
                    await kb_barber_choice (barber_id=barber.id)).as_markup ())

        await state.set_state(EditBarber.start_edit)

    if callback_query.data.split('_')[-1] =='Вернуться назад':
        await state.clear()
        await callback_query.message.edit_text('Админ-панель',reply_markup=Admin_kb.as_markup())

@admin_router.message(StateFilter('*'),Command('отмена'))
@admin_router.message(StateFilter('*'),F.text.casefold() == "отмена")
async def cancel_handler(message:types.Message,state:FSMContext):
    curent_state=await state.get_state()
    if curent_state is None:
        return

    await state.clear ()
    await message.edit_text("Действия отменены",reply_markup=Admin_kb.as_markup())


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddService.add_name:
        await message.answer(
            'Предыдущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AddService.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddBarber.alerts[previous.state]}"
            )
            return
        previous = step



@admin_router.callback_query(EditBarber.start_edit,F.data)
async def edit_barber_start(callback_query:types.CallbackQuery,state:FSMContext):
    if not callback_query.data.split('_')[-1] !='Вернуться назад':
        await state.update_data (barber_id=int(callback_query.data.split('_')[-1]))
    await callback_query.message.edit_reply_markup(reply_markup=(await barber_param_to_change()).as_markup())
    #Здесь нужно продолжить логику изменения параметров
    await state.set_state(EditBarber.choice_what_to_edit)

@admin_router.callback_query(EditBarber.choice_what_to_edit,F.data.startswith('barber_param_edit_'))
async def start_editing_barber(callback_query:types.CallbackQuery,state:FSMContext,session:AsyncSession):
        if callback_query.data.split('_')[-1] == 'Назад':
            data = await state.get_data ()
            await callback_query.message.edit_reply_markup (
                reply_markup=(await kb_barber_choice(data['barber_id'])).as_markup ())
            await state.set_state(EditBarber.start_edit)
            return
        if callback_query.data.split('_')[-1] =='Удалить':
            data=await state.get_data()
            await orm_delete_item(session=session,item_id=data['barber_id'],table=Barbers)
            await callback_query.message.answer('Барбер удален!',reply_markup=Admin_kb.as_markup())
            await state.clear()
            return
        if callback_query.data.split('_')[-1].lower()=='статус':
            await callback_query.message.answer (f'Введите новое {callback_query.data.split ("_") [ -1 ].lower ()}',
                                           reply_markup=choose_barber_status_kb.as_markup())
        else:
            await callback_query.message.answer(f'Введите новое {callback_query.data.split("_")[-1].lower()}',reply_markup=None)

        await state.update_data (what_to_edit=callback_query.data.split('_')[-1])
        await state.set_state(EditBarber.edit)

@admin_router.callback_query(F.data.split('_')[-1].as_('new_barber_status'),EditBarber.edit)
async def change_barber_status(callback_query:types.CallbackQuery,state:FSMContext,session:AsyncSession,new_barber_status:str):

    barber = await state.get_data ()
    barber_id = barber [ 'barber_id' ]
    data = await orm_get_single_item (item_id=barber_id, table=Barbers, session=session)
    old_param = data.status

    if new_barber_status == experience.an_experienced.value:
        barber['status'] = experience.an_experienced
    elif new_barber_status == experience.beginner.value:
        barber['status'] = experience.an_experienced

    barber [ 'name' ] = data.name
    barber [ 'description' ] = data.description

    barber [ 'photo' ] = data.photo

    await orm_update_barber (data=barber, barber_id=barber_id, session=session)
    await state.clear ()
    await callback_query.message.answer (f'{old_param} --> {new_barber_status}', reply_markup=Admin_kb.as_markup ())

@admin_router.message (F.text.as_ ('new_barber_param') | F.photo[-1].file_id.as_('new_barber_param'), EditBarber.edit)
async def change_param_barber (message: types.CallbackQuery, state: FSMContext, session: AsyncSession,
                             new_barber_param: str):

    barber = await state.get_data ()
    barber_id = barber [ 'barber_id' ]
    data = await orm_get_single_item (item_id=barber_id, table=Barbers, session=session)
    param = barber [ 'what_to_edit' ]
    old_param = ''

    if param == 'Имя':
        old_param = data.name
        data.name = new_barber_param
        barber['name']=new_barber_param
        barber['status']=data.status
        barber['description']=data.description
        barber['photo']=data.photo

    elif param == 'Описание':
        old_param = data.description
        data.description = new_barber_param
        barber[ 'name' ] = data.name
        barber['description']=new_barber_param
        barber [ 'status' ] = data.status
        barber [ 'photo' ] = data.photo

    elif param == 'Фото':
        old_param = data.photo
        data.photo = new_barber_param
        barber [ 'name' ] = data.name
        barber [ 'description' ] = data.description
        barber [ 'status' ] = data.status
        barber['photo']=new_barber_param





    await orm_update_barber (data=barber, barber_id=barber_id, session=session)
    await state.clear()
    await message.answer (f'{old_param} --> {new_barber_param}', reply_markup=Admin_kb.as_markup())










@admin_router.message(F.text.as_('barber_name'),AddBarber.add_name)
async def add_barber_name(message:types.Message,state:FSMContext,barber_name:str):
    if 4 >= len (message.text) >= 150:
        await message.answer (
                "Имя барбера не должно превышать 150 символов\nили быть менее 5ти символов.\nВведите заново"
        )
        return

    await state.update_data (name=barber_name)

    await message.answer (f'Выберите статус',reply_markup=choose_barber_status_kb.as_markup())
    await state.set_state (AddBarber.add_status)



@admin_router.message(AddBarber.add_name)
async def add_barber_name1(message:types.Message):
    await message.answer (f'Вы ввели недопустимые данные, введите имя барбера')


@admin_router.callback_query(F.data,AddBarber.add_status)
async def add_barber_status(callback_query:types.CallbackQuery,state:FSMContext):
    if callback_query.data.split('_')[-1] != 'skip':

        #status_=expirience.__getitem__(callback_query.data.split('_')[-1])
        status_='error'
        if callback_query.data.split('_')[-1]==experience.beginner.value:
            status_=experience.beginner

        elif callback_query.data.split('_')[-1]==experience.an_experienced.value:
            status_=experience.an_experienced

        await state.update_data(status=status_)
    await callback_query.message.answer("Теперь отправьте фото барбера")
    await state.set_state(AddBarber.add_photo)

@admin_router.message(F.text,AddBarber.add_status)
async def add_barber_status1(message:types.Message,state:FSMContext):

    await message.answer(text="Вы ввели недопустимые данные, выберите статус используя клавиатуру",reply_markup=choose_barber_status_kb.as_markup())




@admin_router.message (F.photo, AddBarber.add_photo)
async def add_photo (message:types.Message, state: FSMContext):
    await state.update_data (photo=message.photo[ -1 ].file_id)
    await message.answer (f'Введите описание')
    await state.set_state (AddBarber.add_descriprtion)

@admin_router.message(AddBarber.add_photo)
async def add_service_photo1 (message: types.Message, state: FSMContext):
    await message.answer (f'Вы ввели недопустимые данные, отправьте фотографию барбера')


@admin_router.message (F.text.as_('barber_description'), AddBarber.add_descriprtion)
async def add_barebr_description (message: types.Message, state: FSMContext, barber_description:str,session:AsyncSession):
    await state.update_data (description=barber_description)
    data=await state.get_data()


    await orm_add_barber(session,data)
    await message.answer(f"Барбер добавлен", reply_markup=Admin_kb.as_markup())
    await state.clear()


@admin_router.message (AddBarber.add_descriprtion)
async def add_barber_description1 (message: types.Message, state: FSMContext, service_price:str):
    await message.answer (f'Вы ввели недопустимые данные, отправьте описание барбера')
