from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from globals import *
from state import states, StateFilter
from database import add_schedule
from utils import CallbackFilter, get_user_id, answer, parse_date
from classes import Post, CantBeMixed, State
from menus import channel_menu

# Генерации клавиатуру для редактирование
def create_write_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='📰 Опубликовать', callback_data='publish_post'), InlineKeyboardButton(text='👁️ Предпросмотр', callback_data='preview_post'))
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
    text = '➕ Кнопка добавлена'
    if len(states[get_user_id(message)].post.media) > 1:
        text += '\n\nP.S. Инлайн Кнопки не поддерживается при множественных медиа - Ограничение Telegram 😒'
    await answer(message, text, reply_markup=create_write_keyboard().as_markup())

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
    states[get_user_id(query)].post = Post()
    await answer(query, text="Отправьте новый текст или файлы для изменения поста.", reply_markup=create_write_keyboard().as_markup())

# Обработчик текстовых сообщений
@dp.message(F.text, StateFilter('writing_post'))
async def handle_text(message: Message):
    states[get_user_id(message)].post.text = message.html_text
    # Здесь можно добавить логику для сохранения текста и предварительного просмотра
    await answer(message, text="Текст получен. Отправьте медиафайлы.", reply_markup=create_write_keyboard().as_markup())

# Обработчик фоток
@dp.message(F.photo, StateFilter('writing_post'))
async def handle_media(message: Message):
    try:
        states[get_user_id(message)].post.add_media(('photo', message.photo[-1].file_id))
    except CantBeMixed:
        await answer(message, text="Невозможно добавить фотографию, так как уже прикреплен медиа другого типа", reply_markup=create_write_keyboard().as_markup())
        return
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await answer(message, text="Медиафайл получен. Готов к публикации.", reply_markup=create_write_keyboard().as_markup())

# Обработчик документов
@dp.message(F.document, StateFilter('writing_post'))
async def handle_media(message: Message):
    try:
        states[get_user_id(message)].post.add_media(('document', message.document.file_id))
    except CantBeMixed:
        await answer(message, text="Невозможно добавить документ, так как уже прикреплен медиа другого типа", reply_markup=create_write_keyboard().as_markup())
        return
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await answer(message, text="Документ получен. Готов к публикации.", reply_markup=create_write_keyboard().as_markup())

# Обработчик документов
@dp.message(F.video, StateFilter('writing_post'))
async def handle_media(message: Message):
    try:
        states[get_user_id(message)].post.add_media(('video', message.video.file_id))
    except CantBeMixed:
        await answer(message, text="Невозможно добавить видео, так как уже прикреплен медиа другого типа", reply_markup=create_write_keyboard().as_markup())
        return
    # Здесь можно добавить логику для сохранения медиафайлов и предварительного просмотра
    await answer(message, text="Видео получен. Готов к публикации.", reply_markup=create_write_keyboard().as_markup())
