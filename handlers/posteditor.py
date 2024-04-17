from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton
from aiogram.filters import Command
from aiogram.filters.state import State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from utils import answer, is_media
import asyncio

from globals import *
import constants
from .channel import channel_menu

waitingPostState = State('watingPost', 'posteditor')
postState = State('post', 'posteditor')

@dp.callback_query(constants.callbacks.EditCreatedPost.filter())
async def waiting_post_callback(query: CallbackQuery, state: FSMContext, callback_data: constants.callbacks.EditCreatedPost):
    await state.set_state(waitingPostState)
    await state.set_data({
        'chat_id': callback_data.chat_id,
    })
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data=constants.callbacks.CANCEL))
    await answer(query, '😋 Перешли сообщеине, которое необходимо отредакторивать', reply_markup=keyboard.as_markup())

@dp.callback_query(waitingPostState, F.data == constants.callbacks.CANCEL)
async def cancel_callback(query: CallbackQuery, state: FSMContext):
    chat_id = (await state.get_data())['chat_id']
    await state.clear()
    await channel_menu(query, chat_id=chat_id)

@dp.callback_query(postState, F.data == constants.callbacks.CANCEL)
async def cancel_callback(query: CallbackQuery, state: FSMContext):
    chat_id = (await state.get_data())['chat_id']
    await state.clear()
    await channel_menu(query, chat_id=chat_id)

@dp.message(waitingPostState, F.forward_from_chat)
async def get_forwaded_message(message: Message, state: FSMContext):
    chat_id = (await state.get_data())['chat_id']
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data=constants.callbacks.CANCEL))
    if chat_id != message.forward_from_chat.id:
        await answer(message, '😒 Это не сообщение выбранного канала', reply_markup=keyboard.as_markup())
        return
    try:
        if not is_media(message):
            await bot.edit_message_text(text=message.html_text, message_id=message.forward_from_message_id, parse_mode='html', chat_id=chat_id)
        else:
            await bot.edit_message_caption(caption=message.html_text, message_id=message.forward_from_message_id, parse_mode='html', chat_id=chat_id)
    except TelegramBadRequest as d:
        if 'message is not modified' not in d.message:
            await answer(message, '😒 Я не в силах это отредактировать', reply_markup=keyboard.as_markup())
            return
    await state.set_state(postState)
    await state.set_data({
        'chat_id': chat_id,
        'message_id': message.forward_from_message_id,
        'is_media': is_media(message),
    })
    await answer(message, 'Введите новый только текст', reply_markup=keyboard.as_markup())


@dp.message(postState, F.text)
async def get_new_message(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    message_id = data['message_id']
    is_media = data['is_media']
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='Отмена', callback_data=constants.callbacks.CANCEL))
    try:
        if not is_media:
            await bot.edit_message_text(text=message.html_text, message_id=message_id, parse_mode='html', chat_id=chat_id)
        else:
            await bot.edit_message_caption(caption=message.html_text, message_id=message_id, parse_mode='html', chat_id=chat_id)
    except TelegramBadRequest as d:
        print(d)
        await answer(message, '😒 Я что-то не смог поменять', reply_markup=keyboard.as_markup())
        return
    await state.clear()
    await answer(message, text='Пост отредактирован')
    await asyncio.sleep(1)
    await channel_menu(message, chat_id=chat_id)

