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
from database import link_chat_to_user, get_links_of_user, is_linked, unlink_chat_from_user, add_schedule
from utils import CallbackFilter, is_user_admin, get_user_id, answer, Context, parse_date
from classes import Post, State
import scheduler

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

# Генерации клавиатуру для редактирование
def create_write_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='📰 Опубликовать', callback_data='publish_post'))
    keyboard = keyboard.row(InlineKeyboardButton(text='👁️ Предпросмотр', callback_data='preview_post'))
    keyboard = keyboard.row(InlineKeyboardButton(text='🩹 Очистить', callback_data='rewrite_post'))
    keyboard = keyboard.row(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_post'))
    return keyboard


# Функция при нажатие для созданиие поста
@dp.callback_query(CallbackFilter('write_post'), StateFilter('channel'))
async def write_post_callback(query: CallbackQuery): 
    states[get_user_id(query)] = State(
        'writing_post',
        chat_id=states[get_user_id(query)].chat_id,
        post=Post()
    )
    await answer(query, text='👍 Режим написание поста\n\nОтправьте фото или текст\n\n', reply_markup=create_write_keyboard().as_markup())

@dp.callback_query(CallbackFilter('unlink_channel'), StateFilter('channel'))
async def unlink_channel_callback(query: CallbackQuery):
    unlink_chat_from_user(get_user_id(query), states[get_user_id(query)].chat_id)
    await channels_menu(query)

# функция для показа текущего поста
@dp.callback_query(StateFilter('writing_post'), CallbackFilter('preview_post'))
async def show_current_post(query: CallbackQuery):
    if states[get_user_id(query)].post.is_empty():
        await answer(query, "Пост пустой.", reply_markup=create_write_keyboard().as_markup())
        return
    else:
        await query.answer()
    await states[get_user_id(query)].post.send(get_user_id(query))
    await bot.send_message(chat_id=get_user_id(query), text='👁️ Предпросмотр', reply_markup=create_write_keyboard().as_markup())

# Обработчик команды /publish
@dp.callback_query(StateFilter('writing_post'), CallbackFilter('publish_post'))
async def publish_command(query: CallbackQuery):
    if states[get_user_id(query)].post.is_empty():
        await answer(query, "Пост пустой.", reply_markup=create_write_keyboard().as_markup())
        return
    # Здесь можно добавить логику для публикации сохранённого поста
    await answer(query, "Пост опубликован.")
    # Временаня логика отправки в канал
    await states[get_user_id(query)].post.send(states[get_user_id(query)].chat_id)
    await channel_menu(query)

# Обработчик команды /cancel
@dp.callback_query(StateFilter('writing_post'), CallbackFilter('cancel_post'))
async def publish_command(query: CallbackQuery):
    await channel_menu(query)

# Обработчик команды /button
@dp.message(Command('button'), StateFilter('writing_post'))
async def publish_command(message: Message):
    args = message.text.split()
    if len(args) < 3:
        await answer(message, "❓Как добавить кнопку\n\nПример:\n/button https://bmstu.ru Сайт МГТУ им Н. Э. Баумана")
        return
    states[get_user_id(message)].post.buttons.append([(' '.join(args[2:]), args[1])])
    await answer(message, "➕ Кнопка добавлена")

# Обработчик команды /schedule
@dp.message(Command('schedule'), StateFilter('writing_post'))
async def publish_command(message: Message):
    if states[get_user_id(message)].post.is_empty():
        await message.reply("Пост пустой.")
        return
    args = message.text.split()
    if len(args) < 2 or parse_date(' '.join(args[1:])) is None:
        await answer(message, "❓Как отложить пост\n\nПример:\n/schedule 31.12.2024 23:59")
        return
    add_schedule(states[get_user_id(message)].chat_id, parse_date(' '.join(args[1:])), states[get_user_id(message)].post)
    await answer(message, "⌚ Пост запланирован!")
    await channel_menu(message)

# При нажатие на переписать пост
@dp.callback_query(StateFilter('writing_post'), CallbackFilter('rewrite_post'))
async def rewrite_post_callback(query: CallbackQuery):
    await answer(query, text="Отправьте новый текст или файлы для изменения поста.", reply_markup=create_write_keyboard().as_markup())

# Обработчик текстовых сообщений
@dp.message(F.text, StateFilter('writing_post'))
async def handle_text(message: Message):
    states[get_user_id(message)].post.text = message.md_text
    # Здесь можно добавить логику для сохранения текста и предварительного просмотра
    await answer(message, text="Текст получен. Отправьте медиафайлы.", reply_markup=create_write_keyboard().as_markup())

# Обработчик медиафайлов
@dp.message(F.photo, StateFilter('writing_post'))
async def handle_media(message: Post):
    states[get_user_id(message)].post.photo.append(message.photo[-1].file_id)
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await answer(message, text="Медиафайл получен. Готов к публикации.", reply_markup=create_write_keyboard().as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    scheduler.run()
    asyncio.run(main())
    
