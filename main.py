import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ChatMemberAdministrator, \
    InputFile, Chat
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command, Filter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest


from config import TELEGRAM_TOKEN

states = {}
dict_for_messages = {}
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
        print(x.chat.id == x.from_user.id and x.forward_from_chat is not None,  x.from_user.id in states and states[x.from_user.id]['state'] == 'adding_channel')
        return x.chat.id == x.from_user.id and x.forward_from_chat is not None and x.from_user.id in states and states[x.from_user.id]['state'] == 'adding_channel'
    return check

async def is_user_admin(user_id: int, chat: Chat) -> int:
    admins: list[ChatMemberAdministrator] = []
    try:
        admins = await chat.get_administrators()
    except TelegramForbiddenError as err:
        return 0
    except TelegramBadRequest as err:
        return 0
    client = set(filter(lambda x: x.user.id == user_id and (x.status == ChatMemberStatus.CREATOR or x.can_post_messages), admins))
    if len(client) == 0:
        return 1
    return 2
    

@dp.message(adding_channel_filter())
async def adding_channel_forward(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data='channels'))
    status = await is_user_admin(message.from_user.id, message.forward_from_chat)
    if status == 0:
        await message.answer(text='Я не участник данного канала 😒', reply_markup=keyboard.as_markup())
    elif status == 1:
        await message.answer(text='Ты не админ 😒', reply_markup=keyboard.as_markup())
    else:
        pass
        # await message.answer(text='TODO сделать какую нибудь связь, типо бд', reply_markup=keyboard.as_markup())

# функция для показа текущего поста
@dp.message(Command('preview'))
async def show_current_post(message: types.Message):
    if dict_for_messages['photo']:
        # photo = open('temp.png', 'rb')
        await bot.download(dict_for_messages['photo'].file_id, 'temp.png')
        # change
        await message.answer_photo(photo=open('temp.png', 'rb'), caption=dict_for_messages['text'])
        os.remove('temp.png')
    else:
        await message.answer(text=dict_for_messages['text'])


# Обработчик текстовых сообщений
@dp.message(F.text)
async def handle_text(message: types.Message):
    dict_for_messages['text'] = message.text
    # Здесь можно добавить логику для сохранения текста и предварительного просмотра
    await message.reply("Текст получен. Отправьте медиафайлы.")

# Обработчик медиафайлов
@dp.message(F.photo)
async def handle_media(message: types.Message):
    dict_for_messages['photo'] = message.photo[2]
    print(dict_for_messages['photo'])
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await message.reply("Медиафайл получен. Готов к публикации.")

# Функция для публикации поста
async def publish_post(text, media):
    # Здесь реализуйте логику публикации поста в канал
    pass

# Обработчик команды /publish
@dp.message(Command('publish'))
async def publish_command(message: types.Message):
    # Здесь можно добавить логику для публикации сохранённого поста
    await message.reply("Пост опубликован.")

# # Добавление кнопки к посту
# def add_button(text):
#     keyboard = InlineKeyboardMarkup()
#     button = InlineKeyboardButton(text="Нажми", callback_data="button_pressed")
#     keyboard.add(button)
#     return keyboard
#
# # Обработчик callback-запросов
# @dp.callback_query_handler(lambda c: c.data == "button_pressed")
# async def process_callback_button1(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "Кнопка нажата!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
