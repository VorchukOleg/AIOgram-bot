from aiogram import F
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from state import states, StateFilter, delete_state
from utils import get_user_id, answer, Context, CallbackFilter
from classes import State
from database import unlink_chat_from_user, get_links_of_user
import constants

async def channel_menu(c: Context, chat_id: int | None = None):
    user_id = get_user_id(c)
    states[user_id] = State(
        constants.states.CHANNEL,
        chat_id=chat_id or states[user_id].chat_id
    )
    chat = await bot.get_chat(states[user_id].chat_id)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Написать новый пост', callback_data=constants.callbacks.WRITE_POST))
    keyboard = keyboard.row(InlineKeyboardButton(text='❌ Отвязать', callback_data=constants.callbacks.UNLINK_CHANNEL))
    keyboard = keyboard.row(InlineKeyboardButton(text='📚 Каналы', callback_data=constants.callbacks.CHANNELS))
    await answer(c, text='💻 Канал: ' + chat.full_name + '\n\nЧто вы хотите сделать?', reply_markup=keyboard.as_markup())

async def channels_menu(c: Context):
    keyboard = InlineKeyboardBuilder()
    delete_state(c)
    for linkedChat in await get_links_of_user(get_user_id(c)):
        keyboard = keyboard.row(InlineKeyboardButton(text=linkedChat.full_name, callback_data=constants.callbacks.CHANNEL_PREFIX + str(linkedChat.id)))
    keyboard = keyboard.row(InlineKeyboardButton(text='➕ Добавить канал', callback_data=constants.callbacks.ADD_CHANNELS), InlineKeyboardButton(text='↩️ На главную', callback_data=constants.callbacks.MAIN))
    await answer(c, text='💻 Выберите канал', reply_markup=keyboard.as_markup())

@dp.callback_query(CallbackFilter(constants.callbacks.UNLINK_CHANNEL), StateFilter(constants.states.CHANNEL))
async def unlink_channel_callback(query: CallbackQuery):
    unlink_chat_from_user(get_user_id(query), states[get_user_id(query)].chat_id)
    await channels_menu(query)
