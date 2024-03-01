from aiogram.utils.keyboard import ReplyKeyboardBuilder,ReplyKeyboardMarkup,KeyboardButton


#отправка номера телефона

send_contact = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="📱Отправить", request_contact=True)

    ],
],resize_keyboard=True, one_time_keyboard=True)

#send_contact.add(a1)