from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.models import experience

Admin_kb = InlineKeyboardBuilder()
services=['Услуги','Мастера','Банеры','Отследить записи']
for _ in services:
    Admin_kb.button(text=f"{_}", callback_data=f"admin_{_}")

Admin_kb.adjust(1, 1, 1, 1, 1)



ADD_OR_EDIT_kb= InlineKeyboardBuilder()
services=['Добавить', 'Редактировать', 'Вернуться назад']
for _ in services:
    ADD_OR_EDIT_kb.button(text=f"{_}", callback_data=f"add_or_edit_{_}")

ADD_OR_EDIT_kb.adjust(1, 1, 1)


async def service_param_to_change():
    service=InlineKeyboardBuilder()
    options = [ 'Название', 'Описание', 'Цена','Фото','Удалить','Назад' ]
    for _ in options:
        service.button (text=f"{_}", callback_data=f"service_param_edit_{_}")

    service.adjust (1, 1, 1, 1)
    return service



ADD_OR_EDIT_Barbers_kb = InlineKeyboardBuilder()
options=['Добавить', 'Редактировать', 'Вернуться назад']
for _ in options:
    ADD_OR_EDIT_Barbers_kb.button(text=f"{_}", callback_data=f"add_barbers_or_edit_{_}")

ADD_OR_EDIT_Barbers_kb.adjust(1, 1, 1)





choose_barber_status_kb=InlineKeyboardBuilder()

statuses=[]
statuses.append('🦈Барбер-мастер')
statuses.append('🎓Стажор')
for status in statuses:
    choose_barber_status_kb.button(text=f'{status}',callback_data=f'barber_status_{status}')
choose_barber_status_kb.button(text=f'Оставить пустым',callback_data=f'barber_status_skip')
choose_barber_status_kb.adjust(2,1)

async def barber_param_to_change():
    barber_param_to_change_kb=InlineKeyboardBuilder()
    options = [ 'Имя', 'Статус', 'Описание','Фото','Удалить','Назад' ]
    for _ in options:
        barber_param_to_change_kb.button (text=f"{_}", callback_data=f"barber_param_edit_{_}")

    barber_param_to_change_kb.adjust (1, 1, 1, 1)
    return barber_param_to_change_kb


