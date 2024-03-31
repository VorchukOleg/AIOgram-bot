import asyncio
import logging
import sys
from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from database import link_chat_to_user, get_links_of_user, is_linked
from utils import clbk_filter, is_user_admin

# Словарь состояние... Это состаяние в котором бот находится бот для каждого пользователи поотдельности
states = {}
# Может dict_for_messages объединить с states - фактически у них общая задача - хранить значение общение с ботом
dict_for_messages = {}

# Функция которая запускается при Старте
@dp.message(CommandStart())
async def start_command(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.add(InlineKeyboardButton(text='✍️ Каналы', callback_data='channels'))
    text = '💻 Привет'
    # Условие необходимое для проверки, это сообщение бота или человека (т.к. данная функция вызывается и тут и через callback_main)
    if message.from_user.id == bot.id:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.answer(text, reply_markup=keyboard.as_markup())

# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'channels')
@dp.callback_query(clbk_filter('channels'))
async def channels_callback(query: CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    for linkedChat in await get_links_of_user(query.from_user.id):
        keyboard = keyboard.row(InlineKeyboardButton(text=linkedChat.full_name, callback_data='channel_' + str(linkedChat.id)))
    keyboard = keyboard.row(InlineKeyboardButton(text='➕ Добавить канал', callback_data='add_channel'), InlineKeyboardButton(text='↩️ На главную', callback_data='main'))
    await query.message.edit_text(text='💻 Выберите канал', reply_markup=keyboard.as_markup())

# Функция управление привязанным каналом
@dp.callback_query(lambda x: x.data.startswith('channel_'))
async def channel_open_callback(query: CallbackQuery):
    chat = await is_linked(query.from_user.id, int(query.data[len('channel_'):]))
    keyboard = InlineKeyboardBuilder()
    if chat is None:
        keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Каналы', callback_data='channels'))
        await query.message.edit_text(text='❌ Нет доступа', reply_markup=keyboard.as_markup())
        return
    states[query.from_user.id] = {
        'state': 'channel',
        'chat_id': chat.id
    }
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Написать новый пост', callback_data='write_post'))
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Каналы', callback_data='channels'))
    await query.message.edit_text(text='💻 Канал: ' + chat.full_name + '\n\nЧто вы хотите сделать?', reply_markup=keyboard.as_markup())


# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'add_channel')
@dp.callback_query(clbk_filter('add_channel'))
async def add_channel(query: CallbackQuery):
    states[query.from_user.id] = {
        'state': 'adding_channel'
    }
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data='channels'))
    await query.message.edit_text(text='➕ Добавление канала\n\n1) Добавьте меня в канал\n2) Перешлите суда одно сообщение из канала', reply_markup=keyboard.as_markup())

# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'main')
@dp.callback_query(clbk_filter('main'))
async def callback_main(query: CallbackQuery): 
    await start_command(query.message)

# Это достаточно сложный фильтр которые занимается подменю... (см на ф-ию adding_channel_forward)
def adding_channel_filter():
    def check(x: Message):
        return x.chat.id == x.from_user.id and x.forward_from_chat is not None and x.from_user.id in states and states[x.from_user.id]['state'] == 'adding_channel'
    return check
    
# По моей идеи, можно будет к боту привязыватся тг каналы, и для этого нужно подменю
@dp.message(adding_channel_filter())
async def adding_channel_forward(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='В меню', callback_data='channels'))
    status = await is_user_admin(message.from_user.id, message.forward_from_chat)
    if status == 0:
        await message.answer(text='Я не участник данного канала 😒', reply_markup=keyboard.as_markup())
    elif status == 1:
        await message.answer(text='Ты не админ 😒', reply_markup=keyboard.as_markup())
    else:
        link_chat_to_user(message.from_user.id, message.forward_from_chat.id)
        await message.answer(text='😊 Канал привязан, теперь вы можете писать посты', reply_markup=keyboard.as_markup())

# функция для показа текущего поста
@dp.message(Command('preview'))
async def show_current_post(message: Message):
    if dict_for_messages['photo']:
        await bot.send_photo(chat_id=message.chat.id, photo=dict_for_messages['photo'], caption=dict_for_messages['text'])
    else:
        await message.answer(text=dict_for_messages['text'])

# Обработчик команды /publish
@dp.message(Command('publish'))
async def publish_command(message: Message):
    # Здесь можно добавить логику для публикации сохранённого поста
    await message.reply("Пост опубликован.")

# Обработчик текстовых сообщений
@dp.message(F.text)
async def handle_text(message: Message):
    dict_for_messages['text'] = message.text
    # Здесь можно добавить логику для сохранения текста и предварительного просмотра
    await message.reply("Текст получен. Отправьте медиафайлы.")

# Обработчик медиафайлов
@dp.message(F.photo)
async def handle_media(message: Message):
    dict_for_messages['photo'] = message.photo[2].file_id
    print(dict_for_messages['photo'])
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await message.reply("Медиафайл получен. Готов к публикации.")

# Функция для публикации поста
async def publish_post(text, media):
    # Здесь реализуйте логику публикации поста в канал

    pass

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
    
