from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import TELEGRAM_TOKEN
from statemanager import StateManager

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher()
sm = StateManager(bot)

from states.main import Main

@dp.message(CommandStart())
async def start_command(message: Message):
    await sm.set_state(message.chat.id, Main())

@dp.message()
async def on_message(message: Message):
    state = sm.state(message.chat.id)
    if state != None:
        await state.on_message(message)

@dp.callback_query()
async def on_message(query: CallbackQuery):
    state = sm.state(query.message.chat.id)
    if state != None:
        await state.on_callback(query)