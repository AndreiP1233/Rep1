import datetime

from datetime import timedelta

from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.triggers.date import DateTrigger

from database.models import Jobs
from database.orm_query import add_person, get_people_info, add_job

from config import TOKEN

router = Router()
bot = Bot(token = TOKEN)

# POSTGRES_URL = 'postgresql+psycopg2://postgres:Yadebil_1337@localhost:5432/reminder'

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}
scheduler = AsyncIOScheduler(jobstores=jobstores)
scheduler.configure(jobstores=jobstores)

#Установка напоминаний
async def remind(user_id, cur_person):
    try:
        await bot.send_message(user_id, f'{cur_person.date} день рождения у {cur_person.name}! Не забудьте купить подарок (если, конечно, хотите).')
    except Exception as e:
        await bot.send_message(f'Ошибка отправки напоминания: {str(e)}')


async def set_reminds(message:Message, session, user_id):
    people = await get_people_info(session, user_id=message.from_user.id)
    cur_person = people[-1]
    birthday_str = f"{cur_person.date}.{datetime.datetime.now().year}"

    birthday_date = datetime.datetime.strptime(birthday_str, "%d.%m.%Y")
    birthday_week_before_date = datetime.datetime.strptime(birthday_str, "%d.%m.%Y")-timedelta(weeks=1)
    birthday_day_before_date = datetime.datetime.strptime(birthday_str, "%d.%m.%Y")-timedelta(minutes=2)

    bd_dates = [birthday_date, birthday_week_before_date, birthday_day_before_date]    

    for index, item in enumerate(bd_dates):
        if item < datetime.datetime.now():
            item = item.replace(year=item.year + 1)

        try:
            job=scheduler.add_job(
                remind,
                DateTrigger(run_date=item),
                args=[user_id, cur_person],
                jobstore='default'
            )

            await add_job(session, job_id=job.id, person_id=cur_person.id)
            
            if index == 0:
                await message.answer(f'Напоминание о дне рождения {cur_person.name} установлено!')
            if index == 1:
                await message.answer(f'Напоминание за неделю до дня рождения {cur_person.name} установлено!')
            if index == 2:
                await message.answer(f'Напоминание за день до дня рождения {cur_person.name} установлено!')
        except Exception as e:
            await message.answer(f'Ошибка установки напоминания: {str(e)}')

    for job in scheduler.get_jobs():
        print(f"Job loaded: {job}")


#Запуск функции напоминаний
async def start_reminder(message:Message, session:AsyncSession):
    await set_reminds(message, session, user_id=message.from_user.id)

    try:
        scheduler.start()
    except:
        print('ПЛАНИРОВЩИК УЖЕ ЗАПУЩЕН!')

# def init_scheduler():
#     global scheduler
#     scheduler.configure(jobstores=jobstores)
#     try:
#         scheduler.start()
#         print('Планировщик запущен и задания загружены из базы данных.')
#     except Exception as e:
#         print('Ошибка запуска планировщика:', e)

# init_scheduler()

#Вывод списка напоминаний
async def list_reminds(message:Message):
    jobs = scheduler.get_jobs()
    print(f'Список задач: {jobs}')
    if not jobs:
        await message.answer("Нет установленных напоминаний.")
    else:
        reminders = []
        for job in jobs:
            run_date = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
            reminder = f'Напоминание на {run_date}'
            reminders.append(reminder)
        await message.answer('\n'.join(reminders))