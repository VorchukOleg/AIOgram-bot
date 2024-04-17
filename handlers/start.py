from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from state import delete_state
from utils import CallbackFilter, answer
import constants

@dp.message(CommandStart())
async def start_command(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.add(InlineKeyboardButton(text='📚 Каналы', callback_data=constants.callbacks.CHANNELS))
    text = '💻 Привет'
    delete_state(message)
    await answer(message, text=text, reply_markup=keyboard.as_markup())

@dp.callback_query(CallbackFilter(constants.callbacks.MAIN))
async def callback_main(query: CallbackQuery): 
    await start_command(query.message)
