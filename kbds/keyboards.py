from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.orm_query import get_people_info

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить запись')],
        [KeyboardButton(text='Показать список напоминаний')],
        [KeyboardButton(text='Показать список людей')]
    ],
        resize_keyboard=True,
        input_field_placeholder='Что вы хотите сделать?'
    )

def get_people_kb(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    
    return keyboard.adjust(*sizes).as_markup()

async def cancel_kb():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='prev_step'),
                 InlineKeyboardButton(text='Отмена', callback_data='cancel_add'))
    return keyboard.adjust(2,).as_markup()

# def get_callback_btns(
#     *,
#     btns: dict[str, str],
#     sizes: tuple[int] = (2,)):

#     keyboard = InlineKeyboardBuilder()

#     for text, data in btns.items():

#         keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

#     return keyboard.adjust(*sizes).as_markup()
