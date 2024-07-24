import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.reminders import start_reminder, list_reminds, scheduler
from database.orm_query import update_person, delete_job, add_person, get_people_info, get_person_data, delete_person, add_job, get_person_jobs

from kbds.keyboards import main, get_people_kb, cancel_kb

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TOKEN

router = Router()
bot = Bot(token = TOKEN)

#Установка состояний
class Setperson(StatesGroup):
    name = State()
    year = State()
    date = State()

    texts = {
        "Setperson:name": 'Введите имя человека',
        "Setperson:year": 'Введите год рождения',
        "Setperson:date": 'Введите день и месяц рождения в формате ДД.ММ',
    }

#команда старт
@router.message(CommandStart())
async def cmd_start(message:Message):
    await message.answer('Приветствую! Выберите действие⤵️', reply_markup=main)

#вывод нынешней даты
@router.message(Command('todayis'))
async def today_date(message:Message):
    await message.answer('Сегодняшняя дата: ' + str(datetime.date.today()))

#FSM для ввода информации о человеке

@router.callback_query(F.data == 'cancel_add')
async def cancel_handler(callback:CallbackQuery, state:FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        return
    
    await state.clear()
    await callback.message.answer('Действия отменены')
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == 'prev_step')
async def back_handler(callback:CallbackQuery, state:FSMContext):
    current_state = await state.get_state()

    previous = None
    for step in Setperson.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await callback.message.answer(f"Вы вернулись к предыдущему шагу \n{Setperson.texts[previous.state]}")
            return
        previous = step

    await callback.message.answer("Вы вернулись к предыдущему шагу")

@router.message(Command('setperson'))
@router.message(F.text == 'Добавить запись')
async def set_name(message:Message, state: FSMContext):
    await state.set_state(Setperson.name)
    await message.answer(
        'Введите имя человека',
        reply_markup=get_people_kb(
            btns={
                'Отмена':'cancel_add'
            },
            sizes=(1,)
        ))

@router.message(Setperson.name)
async def person_name(message:Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Setperson.year)
    await message.answer(
        'Введите год рождения',
        reply_markup= await cancel_kb())

@router.message(Setperson.year)
async def person_year(message:Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(Setperson.date)
    await message.answer(
        'Введите день и месяц рождения в формате ДД.ММ',
        reply_markup= await cancel_kb())


@router.message(Setperson.date)
async def person_date(message:Message, state: FSMContext, session:AsyncSession):
    await state.update_data(date=message.text)
    data = await state.get_data()

    async with session.begin():
        await add_person(session, data, user_id=message.from_user.id)
        session.commit()

    await message.answer(f'Имя: {data["name"]}\nДата рождения: {data["year"]}.{data["date"]}')
    await state.clear()
    await start_reminder(message, session)

#Получение информации
@router.message(Command('getpeople'))
@router.message(F.text == 'Показать список людей')
async def get_people(message:Message, session):
    people = await get_people_info(session, user_id=message.from_user.id)
    # keyboard=[]
    btns = InlineKeyboardBuilder()
    if people:
        for person in people:
            btn = InlineKeyboardButton(
                text=f'{person.name}',
                callback_data=f'get_person_{person.id}',
                )
            btns.add(btn)
        kb = btns.adjust(2).as_markup()
        print(f"Вот клавиатура:{kb}")
        await message.answer(
                'Выберите человека',
                reply_markup=kb)
    else:
        await message.answer('Список пуст. Добавьте запись!')

@router.callback_query(F.data.startswith('get_person_'))
async def get_person(callback:CallbackQuery, session:AsyncSession):
    person_id = callback.data.split("_")[-1]
    person = await get_person_data(session, person_id)
    await callback.message.edit_text(
        f'{person.name}, {person.date}.{person.year}\nВыберите действие:',
        reply_markup=get_people_kb(
            btns={
                'Изменить запись':f'update_note',
                'Удалить запись':f'delete_{person_id}',
            },
            sizes=(1,)
        ))

@router.callback_query(F.data.startswith('delete_'))
async def delete_note(callback:CallbackQuery, session:AsyncSession):
    person_id = callback.data.split("_")[-1]

    person_jobs = await get_person_jobs(session, person_id)
    for job in person_jobs:
        scheduler.remove_job(f'{job.job_id}')

    await delete_job(session, person_id)
    await delete_person(session, person_id)
    await callback.message.edit_text('Запись и все связанные с ней напоминания удалены')

@router.callback_query(F.data == 'update_note')
async def update_note(callback:CallbackQuery, session:AsyncSession):
    await callback.message.edit_text(
        'Что хотите изменить?',
        reply_markup=get_people_kb(
            btns={
                'Изменить имя':f'update_name',
                'Изменить дату':f'update_date',
            },
            sizes=(1,)
        ))

# @router.callback_query(F.data == 'update_name')
# async def update_name(callback:CallbackQuery, session:AsyncSession):
#     person = await get_person_data(session, person_id)


#Вывод списка напоминаний
@router.message(Command('listreminds'))
@router.message(F.text == 'Показать список напоминаний')
async def call_list(message:Message):
    await list_reminds(message)