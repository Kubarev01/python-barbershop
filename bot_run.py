import os
import sys
import logging
import asyncio
from datetime import datetime

from aiogram import Bot,Dispatcher,Router

import functions.google_calendar
from database import engine
from database.engine import session_maker,engine
from filters.chat_type import ChatTypeFilter, isAdmin
from handlers.admin import admin_router
from handlers.client import user
from handlers.user_group import user_group_router

from dotenv import load_dotenv,find_dotenv
from middleware.db import DataBaseSession
load_dotenv(find_dotenv())
import database.engine


ALLOWED_UPDATES=['message','edited_message','callback_query']

bot = Bot (token=str(os.getenv('TOKEN')))
bot.my_admins_list=[]

dp = Dispatcher ()






dp.include_router(user)
dp.include_router(user_group_router)
dp.include_router(admin_router)



async def on_startup(bot):
    print ('bot is carring out')
    await database.engine.create_db()




async def on_shutdown(bot):
    print('бот лег')



async def main():
    dp.startup.register (on_startup)
    dp.shutdown.register (on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    #await functions.google_calendar.looking_for_free_events_for_barber(barber='Женя')
    #data={'service':'стрижка подростка','date_time':[datetime(2024, 3, 19, 16, 00, 00)],'client_email':'kubarevegor@yandex.ru','description':'fdsf'}
    #await functions.google_calendar.create_event(data)
    #await functions.google_calendar.send_upcomming_events()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot,allowed_updates=ALLOWED_UPDATES)

if __name__=='__main__':
    asyncio.run(main())