import asyncio
import logging
import sys
from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from state import states, StateFilter, delete_state
from database import link_chat_to_user, get_links_of_user, is_linked, unlink_chat_from_user, AlreadyLinked
from utils import CallbackFilter, is_user_admin, get_user_id, answer, Context, parse_date
from classes import State
from menus import channel_menu, channels_menu
import scheduler
import constants

# Функция которая запускается при Старте
@dp.message(CommandStart())
async def start_command(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.add(InlineKeyboardButton(text='📚 Каналы', callback_data=constants.callbacks.CHANNELS))
    text = '💻 Привет'
    delete_state(message)
    await answer(message, text=text, reply_markup=keyboard.as_markup())


# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'channels')
@dp.callback_query(CallbackFilter(constants.callbacks.CHANNELS))
async def channels_callback(query: CallbackQuery):
    await channels_menu(query)

# Функция управление привязанным каналом
@dp.callback_query(lambda x: x.data.startswith(constants.callbacks.CHANNEL_PREFIX))
async def channel_open_callback(query: CallbackQuery):
    chat = await is_linked(query.from_user.id, int(query.data[len(constants.callbacks.CHANNEL_PREFIX):]))
    keyboard = InlineKeyboardBuilder()
    if chat is None:
        keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Каналы', callback_data=constants.callbacks.CHANNELS))
        await query.message.edit_text(text='❌ Нет доступа', reply_markup=keyboard.as_markup())
        return
    await channel_menu(query, chat.id)


# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'add_channel')
@dp.callback_query(CallbackFilter(constants.callbacks.ADD_CHANNELS))
async def add_channel(query: CallbackQuery):
    states[get_user_id(query)] = State(constants.states.ADDING_CHANNEL)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data=constants.callbacks.CHANNELS))
    await query.message.edit_text(text='➕ Добавление канала\n\n1) Добавьте меня в канал\n2) Перешлите суда одно сообщение из канала', reply_markup=keyboard.as_markup())

# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'main')
@dp.callback_query(CallbackFilter(constants.callbacks.MAIN))
async def callback_main(query: CallbackQuery): 
    await start_command(query.message)
    
# По моей идеи, можно будет к боту привязыватся тг каналы, и для этого нужно подменю
@dp.message(StateFilter(constants.states.ADDING_CHANNEL))
async def adding_channel_forward(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='В меню', callback_data=constants.callbacks.CHANNELS))
    status = await is_user_admin(get_user_id(message), message.forward_from_chat)
    if status == 0:
        await message.answer(text='Я не участник данного канала 😒', reply_markup=keyboard.as_markup())
    elif status == 1:
        await message.answer(text='Ты не админ 😒', reply_markup=keyboard.as_markup())
    else:
        try:
            link_chat_to_user(get_user_id(message), message.forward_from_chat.id)
            await message.answer(text='😊 Канал привязан, теперь вы можете писать посты', reply_markup=keyboard.as_markup())
        except AlreadyLinked:
            await message.answer(text='😒 Канал уже был привязан', reply_markup=keyboard.as_markup())


import posteditor

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    scheduler.run()
    asyncio.run(main())
    
