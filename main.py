import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, ChatMemberAdministrator
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError


from config import TELEGRAM_TOKEN

states = {}
dp = Dispatcher()
bot = Bot(TELEGRAM_TOKEN)

def clbk_filter(data: str):
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


@dp.callback_query(clbk_filter('channels'))
async def start_channels_callback(query: CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    # keyboard = keyboard.row(InlineKeyboardButton(text='Канал', callback_data='channels'))
    keyboard = keyboard.row(InlineKeyboardButton(text='➕ Добавить канал', callback_data='add_channel'), InlineKeyboardButton(text='↩️ На главную', callback_data='main'))
    await query.message.edit_text(text='💻 Выберите канал', reply_markup=keyboard.as_markup())

@dp.callback_query(clbk_filter('add_channel'))
async def add_channel(query: CallbackQuery):
    states[query.from_user.id] = {
        'state': 'adding_channel'
    }
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data='channels'))
    await query.message.edit_text(text='➕ Добавление канала\n\n1) Добавьте меня в канал\n2) Перешлите суда одно сообщение из канала', reply_markup=keyboard.as_markup())

@dp.callback_query(clbk_filter('main'))
async def callback_main(query: CallbackQuery): 
    await start_command(query.message)


def adding_channel_filter():
    def check(x: Message):
        return x.chat.id == x.from_user.id and x.forward_from_chat is not None and x.from_user.id in states and states[x.from_user.id]['state'] == 'adding_channel'
    return check

@dp.message(adding_channel_filter())
async def adding_channel_forward(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data='channels'))

    admins: list[ChatMemberAdministrator] = []
    try:
        admins = await message.forward_from_chat.get_administrators()
    except TelegramForbiddenError as err:
        await message.answer(text='Я не участник данного канала 😒', reply_markup=keyboard.as_markup())
        return
    client = set(filter(lambda x: x.user.id == message.from_user.id and (x.status == ChatMemberStatus.CREATOR or x.can_post_messages), admins))
    if len(client) == 0:
        await message.answer(text='Ты не админ 😒', reply_markup=keyboard.as_markup())
        return
    await message.answer(text='TODO сделать какую нибудь связь, типо бд', reply_markup=keyboard.as_markup())


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
