import sys
import logging
import asyncio
import os
from aiogram import Bot,Dispatcher,Router

import database.engine
from database import engine
from handlers.client import user
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())



ALLOWED_UPDATES=['message','edited_message','callback_query']

bot = Bot (token=str(os.getenv('TOKEN')))
dp = Dispatcher ()


dp.include_router(user)


async def on_startup(bot):

    run_param = False
    if run_param:
        await database.engine.drop_db()

    await database.engine.create_db()


async def on_shutdown(bot):
    print('бот лег')



async def main():
    dp.startup.register (on_startup)
    dp.shutdown.register (on_shutdown)
    print ('database is connected')
    print (os.getenv ('DB_URL'))
    await bot.delete_webhook(drop_pending_updates=True)
    print('bot is carring out')
    await dp.start_polling(bot,allowed_updates=ALLOWED_UPDATES)

if __name__=='__main__':
    asyncio.run(main())