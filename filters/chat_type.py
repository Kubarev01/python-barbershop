from aiogram import Bot, types
from aiogram.filters import Filter

class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def check(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

class isAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def check(self, event, bot: Bot) -> bool:
        if isinstance(event, types.Message):
            return event.from_user.id in bot.my_admins_list
        elif isinstance(event, types.CallbackQuery):
            return event.message.from_user.id in bot.my_admins_list
        return False
