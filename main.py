import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart


from config import TELEGRAM_TOKEN


dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer('Hello World')

async def main():
    bot = Bot(TELEGRAM_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
