from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from globals import *
from classes.statemanager import delete_state
from utils import get_user_id, answer, Context, CallbackFilter
from database import get_links_of_user
import constants

async def channels_menu(c: Context):
    keyboard = InlineKeyboardBuilder()
    delete_state(c)
    for linkedChat in await get_links_of_user(get_user_id(c)):
        keyboard = keyboard.row(InlineKeyboardButton(text=linkedChat.full_name, callback_data=constants.callbacks.Channel(chat_id=linkedChat.id).pack()))
    keyboard = keyboard.row(InlineKeyboardButton(text='➕ Добавить канал', callback_data=constants.callbacks.ADD_CHANNELS), InlineKeyboardButton(text='↩️ На главную', callback_data=constants.callbacks.MAIN))
    await answer(c, text='💻 Выберите канал', reply_markup=keyboard.as_markup())

@dp.callback_query(CallbackFilter(constants.callbacks.CHANNELS))
async def channels_callback(query: CallbackQuery):
    await channels_menu(query)

