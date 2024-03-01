from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder


service_kb = InlineKeyboardBuilder()
services=['✂Записаться к мастеру','✉Связаться с нами','🔍Отследить мою запись']
for _ in services:
    service_kb.button(text=f"{_}", callback_data=f"service_{_}")

service_kb.adjust(1,1,1)