from aiogram.filters import Filter
from aiogram import Bot, types




class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def call(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types
        
# class isAdmin(Filter):
#     def __init__(self)->None:
#         pass
#
#     async def __call__(self,message:types.Message,bot:Bot)->bool:
#         return message.from_user.id in bot.my_admins_list

class isAdmin (Filter):
    def init (self) -> None:
        pass

    async def __call__ (self, event, bot: Bot) -> bool:
        if isinstance (event, types.Message):
            return event.from_user.id in bot.my_admins_list
        elif isinstance (event, types.CallbackQuery):
            return event.message.from_user.id in bot.my_admins_list
        return False


