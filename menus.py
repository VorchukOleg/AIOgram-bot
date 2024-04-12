from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from state import states
from utils import get_user_id, answer, Context, parse_date
from classes import State
import constants

async def channel_menu(c: Context, chat_id: int | None = None):
    user_id = get_user_id(c)
    states[user_id] = State(
        'channel',
        chat_id=chat_id or states[user_id].chat_id
    )
    chat = await bot.get_chat(states[user_id].chat_id)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Написать новый пост', callback_data='write_post'))
    keyboard = keyboard.row(InlineKeyboardButton(text='❌ Отвязать', callback_data='unlink_channel'))
    keyboard = keyboard.row(InlineKeyboardButton(text='📚 Каналы', callback_data=constants.callbacks.CHANNELS))
    await answer(c, text='💻 Канал: ' + chat.full_name + '\n\nЧто вы хотите сделать?', reply_markup=keyboard.as_markup())
    