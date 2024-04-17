from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton
from aiogram.filters import Command
from aiogram.filters.state import State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from classes.post import Post
from utils import answer
import asyncio

from globals import *
import constants
from database import delete_schedule, add_schedule, update_schedule, get_schedule_direct
from .channel import channel_menu
from utils import parse_date
from classes.exceptions import CantBeMixed

postState = State('post', 'posteditor')
scheduleState = State('scheduleState', 'posteditor')
buttonsState = State('buttons', 'posteditor')

async def create_write_keyboard(state: FSMContext):
    data = await state.get_data()
    edit_mode = data['edit_mode']
    post: Post = data['post']
    keyboard = InlineKeyboardBuilder()
    if edit_mode:
        keyboard = keyboard.row(InlineKeyboardButton(text='📰 Опубликовать прямо сейчас', callback_data=constants.callbacks.PUBLISH_POST))
        keyboard = keyboard.row(InlineKeyboardButton(text='⌚ Переотложить', callback_data=constants.callbacks.SCHEDULE))
        keyboard = keyboard.row(InlineKeyboardButton(text='💾 Сохранить', callback_data=constants.callbacks.SAVE_POST), InlineKeyboardButton(text='🗑️ Удалить', callback_data=constants.callbacks.DELETE_POST))
    else:
        keyboard = keyboard.row(InlineKeyboardButton(text='📰 Опубликовать', callback_data=constants.callbacks.PUBLISH_POST))
        keyboard = keyboard.row(InlineKeyboardButton(text='⌚ Отложить запись', callback_data=constants.callbacks.SCHEDULE))
    if len(post.media) > 1 or (post.text and len(post.media) > 0):
        keyboard = keyboard.row(InlineKeyboardButton(text='🧹 Очистить медиа', callback_data=constants.callbacks.CLEAR_MEDIA))
    if len(post.media) > 0 and post.text:
        keyboard = keyboard.row(InlineKeyboardButton(text='🧹 Очистить текст', callback_data=constants.callbacks.CLEAR_TEXT))
    keyboard = keyboard.row(InlineKeyboardButton(text='⌨️ Установить кнопки', callback_data=constants.callbacks.SET_BUTTONS))
    keyboard = keyboard.row(InlineKeyboardButton(text='❌ Отмена', callback_data=constants.callbacks.CANCEL))
    return keyboard

@dp.callback_query(constants.callbacks.WritePost.filter())
async def write_post_callback(query: CallbackQuery, state: FSMContext, callback_data: constants.callbacks.WritePost):
    await state.set_state(postState)
    post: Post
    if callback_data.edit_mode:
        _, post, _ = get_schedule_direct(callback_data.schedule_id)
    else:
        post = Post()
    await state.set_data({
        'post': post,
        'chat_id': callback_data.chat_id,
        'edit_mode': callback_data.edit_mode,
        'schedule_id': callback_data.schedule_id,
    })
    if not callback_data.edit_mode:
        await answer(query, text='👍 Режим написание поста\n\nОтправьте фото или текст\n\n', reply_markup=(await create_write_keyboard(state)).as_markup())
    else:
        await post.send(query.from_user.id, buttons=await create_write_keyboard(state))
@dp.callback_query(postState, F.data == constants.callbacks.CANCEL)
async def cancel_callback(query: CallbackQuery, state: FSMContext):
    chat_id = (await state.get_data())['chat_id']
    await state.clear()
    await channel_menu(query, chat_id)

@dp.callback_query(postState, F.data == constants.callbacks.PUBLISH_POST)
async def publish_command(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post: Post = data['post']
    chat_id = data['chat_id']
    if post.is_empty():
        await answer(query, "Пост пустой.", reply_markup=(await create_write_keyboard(state)).as_markup())
        return
    # Здесь можно добавить логику для публикации сохранённого поста
    await answer(query, "Пост опубликован.")

    await post.send(chat_id)
    if data['edit_mode']:
        delete_schedule(data['schedule_id'])
    
    await asyncio.sleep(1)
    await state.clear()
    await channel_menu(query, chat_id=chat_id)

@dp.callback_query(postState, F.data == constants.callbacks.CLEAR_TEXT)
async def clear_text(query: CallbackQuery, state: FSMContext):
    post: Post = (await state.get_data())['post']
    post.text = None
    await query.answer()
    await post.send(query.from_user.id, buttons=await create_write_keyboard(state))

@dp.callback_query(postState, F.data == constants.callbacks.CLEAR_MEDIA)
async def clear_media(query: CallbackQuery, state: FSMContext):
    post: Post = (await state.get_data())['post']
    if post.text:
        post.media = []
    else:
        post.media = [post.media[0]]
    await query.answer()
    await post.send(query.from_user.id, buttons=await create_write_keyboard(state))

@dp.message(F.text, postState)
async def handle_text(message: Message, state: FSMContext):
    post: Post = (await state.get_data())['post']
    post.text = message.html_text
    await post.send(message.chat.id, buttons=await create_write_keyboard(state))

@dp.message(F.photo, postState)
async def handle_photo(message: Message, state: FSMContext):
    post: Post = (await state.get_data())['post']
    try:
        post.add_media(('photo', message.photo[-1].file_id))
    except CantBeMixed:
        await answer(message, text="Невозможно добавить фотографию, так как уже прикреплен медиа другого типа", reply_markup=create_write_keyboard(message).as_markup())
        return
    await post.send(message.chat.id, buttons=await create_write_keyboard(state))

@dp.message(F.document, postState)
async def handle_photo(message: Message, state: FSMContext):
    post: Post = (await state.get_data())['post']
    try:
        post.add_media(('document', message.document.file_id))
    except CantBeMixed:
        await answer(message, text="Невозможно добавить документ, так как уже прикреплен медиа другого типа", reply_markup=create_write_keyboard(message).as_markup())
        return
    await post.send(message.chat.id, buttons=await create_write_keyboard(state))

@dp.message(F.video, postState)
async def handle_photo(message: Message, state: FSMContext):
    post: Post = (await state.get_data())['post']
    try:
        post.add_media(('video', message.video.file_id))
    except CantBeMixed:
        await answer(message, text="Невозможно добавить видео, так как уже прикреплен медиа другого типа", reply_markup=create_write_keyboard(message).as_markup())
        return
    await post.send(message.chat.id, buttons=await create_write_keyboard(state))

@dp.callback_query(F.data == constants.callbacks.SCHEDULE, postState)
async def publish_command(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post = data['post']
    if post.is_empty():
        await answer(query, "Пост пустой.", reply_markup=(await create_write_keyboard(state)).as_markup())
        return
    await state.set_state(scheduleState)
    await state.set_data(data)
    await answer(query, "❓Как отложить пост\n\nПример:\n`31.12.2024 23:59`\n\nИли напишите /cancel - для отмены")

@dp.message(scheduleState, Command('cancel'))
async def publish_command(message: Message, state: FSMContext):
    data = await state.get_data()
    post: Post = data['post']
    await state.set_state(postState)
    await state.set_data(data)
    await post.send(message.chat.id, buttons=await create_write_keyboard(state))

@dp.message(F.text, scheduleState)
async def publish_command(message: Message, state: FSMContext):
    data = await state.get_data()
    post: Post = data['post']
    chat_id = data['chat_id']
    schedule_id = data['schedule_id']
    edit_mode = data['edit_mode']
    if parse_date(message.text) is None:
        await answer(message, "❓Как отложить пост\n\nПример:\n`31.12.2024 23:59`")
        return
    if not edit_mode:
        add_schedule(chat_id, parse_date(message.text), post)
        await answer(message, "⌚ Пост запланирован!")
    else:
        update_schedule(schedule_id, post, parse_date(message.text))
        await answer(message, "⌚ Пост перезапланирован!")
    await asyncio.sleep(1)
    await state.clear()
    await channel_menu(message)

@dp.callback_query(postState, F.data == constants.callbacks.DELETE_POST)
async def delete_post_callback(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    schedule_id = data['schedule_id']
    delete_schedule(schedule_id)
    await answer(query, "Пост удален.")
    await asyncio.sleep(1)
    await state.clear()
    await channel_menu(query)

@dp.callback_query(postState, F.data == constants.callbacks.SAVE_POST)
async def save_callback(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    schedule_id = data['schedule_id']
    post = data['post']
    if post.is_empty():
        await answer(query, "Пост пустой.")
        return
    update_schedule(schedule_id, post, None)
    await answer(query, "💾 Пост сохранён!")
    await asyncio.sleep(1)
    await state.clear()
    await channel_menu(query)
