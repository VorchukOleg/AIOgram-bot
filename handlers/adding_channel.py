from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from globals import *
from classes.statemanager import states, StateFilter
from database import link_chat_to_user, AlreadyLinked
from utils import CallbackFilter, is_user_admin, get_user_id
from classes.state import State
import constants

# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'add_channel')
@dp.callback_query(CallbackFilter(constants.callbacks.ADD_CHANNELS))
async def add_channel(query: CallbackQuery):
    states[get_user_id(query)] = State(constants.states.ADDING_CHANNEL)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data=constants.callbacks.CHANNELS))
    await query.message.edit_text(text='➕ Добавление канала\n\n1) Добавьте меня в канал\n2) Перешлите суда одно сообщение из канала', reply_markup=keyboard.as_markup())
    
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
