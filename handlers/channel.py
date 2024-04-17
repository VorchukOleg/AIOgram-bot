from aiogram import F
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import asyncio

from globals import *
from classes.statemanager import states, StateFilter
from utils import get_user_id, answer, Context, CallbackFilter
from classes.state import State
from database import unlink_chat_from_user, get_schedule, count_schedule, is_linked
from .channels import channels_menu
import constants

async def channel_menu(c: Context, chat_id: int | None = None):
    user_id = get_user_id(c)
    states[user_id] = State(
        constants.states.CHANNEL,
        chat_id=chat_id or states[user_id].chat_id
    )
    chat = await bot.get_chat(states[user_id].chat_id)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Написать новый пост', callback_data=constants.callbacks.WritePost(chat_id=states[user_id].chat_id, edit_mode=False, schedule_id=None).pack()))
    keyboard = keyboard.row(InlineKeyboardButton(text='🕛 Отложенные', callback_data=constants.callbacks.LOOK_SCHEDULE))
    keyboard = keyboard.row(InlineKeyboardButton(text='📝 Отредактировать существующий', callback_data=constants.callbacks.EditCreatedPost(chat_id=states[user_id].chat_id).pack()))
    keyboard = keyboard.row(InlineKeyboardButton(text='❌ Отвязать', callback_data=constants.callbacks.UNLINK_CHANNEL))
    keyboard = keyboard.row(InlineKeyboardButton(text='📚 Каналы', callback_data=constants.callbacks.CHANNELS))
    await answer(c, text='💻 Канал: ' + chat.full_name + '\n\nЧто вы хотите сделать?', reply_markup=keyboard.as_markup())


@dp.callback_query(CallbackFilter(constants.callbacks.UNLINK_CHANNEL), StateFilter(constants.states.CHANNEL))
async def unlink_channel_callback(query: CallbackQuery):
    unlink_chat_from_user(get_user_id(query), states[get_user_id(query)].chat_id)
    await channels_menu(query)

async def looking_schedule_menu(c: Context):
    user_id = get_user_id(c)
    schedule_id, post, date = get_schedule(states[user_id].chat_id, states[user_id].page)
    if post == None:
        await answer(c, text='Нет отложенных записей 😋')
        await asyncio.sleep(1)
        await channel_menu(c)
        return
    await c.message.delete()
    await post.send(user_id)
    count = count_schedule(states[user_id].chat_id)
    keyboard = InlineKeyboardBuilder()
    keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Отредактировать', callback_data=constants.callbacks.WritePost(chat_id=states[user_id].chat_id, edit_mode=True, schedule_id=schedule_id).pack()))
    if states[user_id].page + 1 <= count:
        keyboard = keyboard.row(InlineKeyboardButton(text='⏭ Дальше', callback_data=constants.callbacks.NEXT_POST))
    if states[user_id].page - 1 >= 1:
        keyboard = keyboard.row(InlineKeyboardButton(text='⏪ Назад', callback_data=constants.callbacks.PREVIOUS_POST))
    keyboard = keyboard.row(InlineKeyboardButton(text='📕 Вернутся в меню канала', callback_data=constants.callbacks.CANCEL))
    await bot.send_message(user_id, text=f'Текущий пост ({states[user_id].page}/{count})\n\nДата: {date.strftime("%d.%m.%Y %H:%M")}', reply_markup=keyboard.as_markup())

@dp.callback_query(CallbackFilter(constants.callbacks.LOOK_SCHEDULE), StateFilter(constants.states.CHANNEL))
async def look_schedule(query: CallbackQuery):
    user_id = get_user_id(query)
    states[user_id] = State(
        constants.states.LOOKING_SCHEDULE,
        chat_id=states[user_id].chat_id,
        page=1,
    )
    await looking_schedule_menu(query)
    

@dp.callback_query(CallbackFilter(constants.callbacks.NEXT_POST), StateFilter(constants.states.LOOKING_SCHEDULE))
async def cancel_looking(query: CallbackQuery):
    states[get_user_id(query)].page += 1
    await looking_schedule_menu(query)

@dp.callback_query(CallbackFilter(constants.callbacks.PREVIOUS_POST), StateFilter(constants.states.LOOKING_SCHEDULE))
async def cancel_looking(query: CallbackQuery):
    states[get_user_id(query)].page -= 1
    await looking_schedule_menu(query)

@dp.callback_query(CallbackFilter(constants.callbacks.CANCEL), StateFilter(constants.states.LOOKING_SCHEDULE))
async def cancel_looking(query: CallbackQuery):
    await channel_menu(query)

@dp.callback_query(constants.callbacks.Channel.filter())
async def channel_open_callback(query: CallbackQuery, callback_data: constants.callbacks.Channel):
    chat = await is_linked(query.from_user.id, callback_data.chat_id)
    keyboard = InlineKeyboardBuilder()
    if chat is None:
        keyboard = keyboard.row(InlineKeyboardButton(text='✍️ Каналы', callback_data=constants.callbacks.CHANNELS))
        await query.message.edit_text(text='❌ Нет доступа', reply_markup=keyboard.as_markup())
        return
    await channel_menu(query, chat.id)
