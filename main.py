import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder


from config import TELEGRAM_TOKEN

states = {}
dp = Dispatcher()
bot = Bot(TELEGRAM_TOKEN)

def fltr(data: str, state: str | None = None):
    if not state == None:
        def check(x: CallbackQuery):
            return x.data == data and x.from_user.id in states and states[x.from_user.id]['state'] == state
        return check
    def check(x: CallbackQuery):
        return x.data == data
    return check

@dp.message(CommandStart())
async def start_command(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.add(InlineKeyboardButton(text='✍️ Каналы', callback_data='channels'))
    text = '💻 Привет'
    if message.from_user.id == bot.id:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.answer(text, reply_markup=keyboard.as_markup())


@dp.callback_query(fltr('channels'))
async def start_channels_callback(query: CallbackQuery):
    states[query.from_user.id] = {
        'state': 'channels'
    }
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Канал', callback_data='channels'))
    keyboard = keyboard.row(InlineKeyboardButton(text='➕ Добавить канал', callback_data='add_channel'), InlineKeyboardButton(text='↩️ На главную', callback_data='main'))
    await query.message.edit_text(text='💻 Выберите канал', reply_markup=keyboard.as_markup())

@dp.callback_query(fltr('main'))
async def callback_main(query: CallbackQuery): 
    await start_command(query.message)


@dp.callback_query()
async def fallback(query: CallbackQuery):
    print(query)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
