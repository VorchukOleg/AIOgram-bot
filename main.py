import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart


from config import TELEGRAM_TOKEN
from statemanager import StateManager

from states.main import Main

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher()
sm = StateManager(bot)

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

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
