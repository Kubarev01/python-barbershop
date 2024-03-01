# from aiogram import Dispatcher,Bot,types,Router,F
# from aiogram.filters import CommandStart,Command
# from dotenv import find_dotenv,load_dotenv
# from filters.chat_type import ChatTypeFilter,isAdmin
#
# import asyncio
# import os
#
# load_dotenv(find_dotenv())
#
#
#
# ALLOWED_UPDATES=['message','edited_message']
#
#
# admin_router= Router(name=__name__)
# admin_router.message.filter(ChatTypeFilter(['private']),isAdmin())
#
#
# @admin_router.message(commands='admin')
# async def admin_check(message:types.Message):
#     pass
#
#
# @admin_router.message(F.from_user.id._in(Admin_ID))
# async def start_cmd(message:types.Message):
#     await bot.send_message(message.from_user.id,f'Привет {message.from_user.username}!\nЯ специальный бот для записи в барбершоп <b>"SHARK"</b>\n'
#                                                 f'Я могу помочь тебе записаться на стрижку или связаться с администартором'
#                                                 f'С чего начнем?',parse_mode='html')