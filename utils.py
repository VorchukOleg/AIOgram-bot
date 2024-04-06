from globals import *
from aiogram.types import CallbackQuery, ChatMemberAdministrator, Chat, Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from datetime import datetime
import re

Context = CallbackQuery | Message

# Функция для создание фильтр (для фитрации данных callback запросов)
def CallbackFilter(data: str):
    def check(x: CallbackQuery):
        return x.data == data
    return check

# Ф-ия проверяет ли человек (в основном кто пишет боту) имеет права писать в канал
# Возвращает 0 - что вообще бот не в канале или не имеет право узнать список админов
# Возвращает 1 - он в канале, но сам человек не админ
# Возвращает 2 - он в канале, и он админ
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

def get_user_id(c: CallbackQuery | Message) -> int:
    user_id: int
    if isinstance(c, CallbackQuery):
        user_id = c.from_user.id
    else:
        user_id = c.chat.id
    return user_id

async def answer(c: CallbackQuery | Message, *args, **kwargs):
    try:
        if isinstance(c, CallbackQuery):
            await c.message.edit_text(*args, **kwargs)
        elif c.from_user.id == bot.id:
            await c.edit_text(*args, **kwargs)
        else:
            await c.answer(*args, **kwargs)
    except TelegramBadRequest:
        if isinstance(c, CallbackQuery):
            await c.answer()


def parse_date(raw: str):
    m = re.search(r'(\d+)\.(\d+).(\d+) (\d+):(\d+)', raw)
    if m is None:
        return None
    date = datetime(
        day=int(m.group(1)),
        month=int(m.group(2)),
        year=int(m.group(3)),
        hour=int(m.group(4)),
        minute=int(m.group(5)),
    )
    return date
