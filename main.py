import asyncio
import logging
import sys
from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from state import states, StateFilter, delete_state
from database import link_chat_to_user, get_links_of_user, is_linked, unlink_chat_from_user
from utils import CallbackFilter, is_user_admin, get_user_id, answer, Context
from classes import Post, State

# Функция которая запускается при Старте
@dp.message(CommandStart())
async def start_command(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.add(InlineKeyboardButton(text='📚 Каналы', callback_data='channels'))
    text = '💻 Привет'
    delete_state(message)
    await answer(message, text=text, reply_markup=keyboard.as_markup())

async def channels_menu(c: Context):
    keyboard = InlineKeyboardBuilder()
    delete_state(c)
    for linkedChat in await get_links_of_user(get_user_id(c)):
        keyboard = keyboard.row(InlineKeyboardButton(text=linkedChat.full_name, callback_data='channel_' + str(linkedChat.id)))
    keyboard = keyboard.row(InlineKeyboardButton(text='➕ Добавить канал', callback_data='add_channel'), InlineKeyboardButton(text='↩️ На главную', callback_data='main'))
    await answer(c, text='💻 Выберите канал', reply_markup=keyboard.as_markup())

# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'channels')
@dp.callback_query(CallbackFilter('channels'))
async def channels_callback(query: CallbackQuery):
    await channels_menu(query)

async def channel_menu(c: Context, chat_id: int | None = None):
    user_id = get_user_id(c)
    states[user_id] = State(
        'channel',
        chat_id=chat_id or states[user_id].chat_id
    )
    chat = await bot.get_chat(states[user_id].chat_id)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Написать новый пост', callback_data='write_post'))
    keyboard = keyboard.row(InlineKeyboardButton(text='❌ Отвязать', callback_data='unlink_channel'))
    keyboard = keyboard.row(InlineKeyboardButton(text='📚 Каналы', callback_data='channels'))
    await answer(c, text='💻 Канал: ' + chat.full_name + '\n\nЧто вы хотите сделать?', reply_markup=keyboard.as_markup())


# Функция управление привязанным каналом
@dp.callback_query(lambda x: x.data.startswith('channel_'))
async def channel_open_callback(query: CallbackQuery):
    chat = await is_linked(query.from_user.id, int(query.data[len('channel_'):]))
    keyboard = InlineKeyboardBuilder()
    if chat is None:
        keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Каналы', callback_data='channels'))
        await query.message.edit_text(text='❌ Нет доступа', reply_markup=keyboard.as_markup())
        return
    await channel_menu(query, chat.id)


# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'add_channel')
@dp.callback_query(CallbackFilter('add_channel'))
async def add_channel(query: CallbackQuery):
    states[get_user_id(query)] = State('adding_channel')
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data='channels'))
    await query.message.edit_text(text='➕ Добавление канала\n\n1) Добавьте меня в канал\n2) Перешлите суда одно сообщение из канала', reply_markup=keyboard.as_markup())

# Функция при нажатие кнопки (при получение callback query если в нём query.data == 'main')
@dp.callback_query(CallbackFilter('main'))
async def callback_main(query: CallbackQuery): 
    await start_command(query.message)
    
# По моей идеи, можно будет к боту привязыватся тг каналы, и для этого нужно подменю
@dp.message(StateFilter('adding_channel'))
async def adding_channel_forward(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='В меню', callback_data='channels'))
    status = await is_user_admin(get_user_id(message), message.forward_from_chat)
    if status == 0:
        await message.answer(text='Я не участник данного канала 😒', reply_markup=keyboard.as_markup())
    elif status == 1:
        await message.answer(text='Ты не админ 😒', reply_markup=keyboard.as_markup())
    else:
        link_chat_to_user(get_user_id(message), message.forward_from_chat.id)
        await message.answer(text='😊 Канал привязан, теперь вы можете писать посты', reply_markup=keyboard.as_markup())

# Функция при нажатие для созданиие поста
@dp.callback_query(CallbackFilter('write_post'), StateFilter('channel'))
async def write_post_callback(query: CallbackQuery): 
    states[get_user_id(query)] = State(
        'writing_post',
        chat_id=states[get_user_id(query)].chat_id,
        post=Post()
    )
    await query.message.edit_text(text='👍 Режим написание поста\n\nОтправьте фото или текст\n\nКоманды:\n/preview - Показать как пост будет выглядить\n/publish - Опубликовать пост\n/cancel - Вернутся в меню настройки канала')

@dp.callback_query(CallbackFilter('unlink_channel'), StateFilter('channel'))
async def unlink_channel_callback(query: CallbackQuery):
    unlink_chat_from_user(get_user_id(query), states[get_user_id(query)].chat_id)
    await channels_menu(query)

# функция для показа текущего поста
@dp.message(Command('preview'), StateFilter('writing_post'))
async def show_current_post(message: Message):
    await states[get_user_id(message)].post.send(message.chat.id)

# Обработчик команды /publish
@dp.message(Command('publish'), StateFilter('writing_post'))
async def publish_command(message: Message):
    # Здесь можно добавить логику для публикации сохранённого поста
    await message.reply("Пост опубликован.")
    # Временаня логика отправки в канал
    await states[get_user_id(message)].post.send(states[get_user_id(message)].chat_id)
    await channel_menu(message)

# Обработчик команды /cancel
@dp.message(Command('cancel'), StateFilter('writing_post'))
async def publish_command(message: Message):
    await channel_menu(message)

# Обработчик текстовых сообщений
@dp.message(F.text, StateFilter('writing_post'))
async def handle_text(message: Message):
    states[get_user_id(message)].post.text = message.md_text
    # Здесь можно добавить логику для сохранения текста и предварительного просмотра
    await message.reply("Текст получен. Отправьте медиафайлы.")

# Обработчик медиафайлов
@dp.message(F.photo, StateFilter('writing_post'))
async def handle_media(message: Post):
    states[get_user_id(message)].post.photo.append(message.photo[-1].file_id)
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await message.reply("Медиафайл получен. Готов к публикации.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
