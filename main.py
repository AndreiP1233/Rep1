import asyncio
import datetime
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from app.handlers import router

from middlewares.db import DataBaseSession
from database.engine import sessionmaker, create_db, drop_db

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.reminders import jobstores

scheduler = AsyncIOScheduler()

bot = Bot(token = TOKEN)
dp = Dispatcher()

async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    
    await create_db()

async def on_shutdown(bot):
    print('Бот лёг спать')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=sessionmaker))

    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')