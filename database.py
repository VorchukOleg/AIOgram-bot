from peewee import *
from globals import bot
from utils import is_user_admin, Chat
from aiogram.exceptions import TelegramForbiddenError
from classes.post import Post
from datetime import datetime

conn = SqliteDatabase('storage.db')

class BaseModel(Model):
    class Meta:
        database = conn

class Linking(BaseModel):
    id = AutoField()
    user_id = BigIntegerField(column_name='UserID')
    chat_id = BigIntegerField(column_name='ChatID')

    class Meta:
        table_name = 'Linking'

class Schedule(BaseModel):
    id = AutoField()
    chat_id = BigIntegerField(column_name='ChatID')
    date = DateTimeField(column_name='Date')
    post = TextField(column_name='Post')

    class Meta:
        table_name = 'Schedule'

class AlreadyLinked(Exception):
    pass

Linking.create_table(True)
Schedule.create_table(True)

def link_chat_to_user(user_id: int, chat_id: int):
    if len(Linking.select().where(Linking.user_id == user_id)) > 0:
        raise AlreadyLinked()
    Linking.create(user_id=user_id, chat_id=chat_id)

async def get_links_of_user(user_id: int) -> list[Chat]:
    links = Linking.select().where(Linking.user_id == user_id)
    chats = []
    for link in links:
        try:
            chat = await bot.get_chat(link.chat_id)
            status = await is_user_admin(user_id, chat)
            if status == 2:
                chats.append(chat)
            else:
                Linking.delete().where(Linking.chat_id == link.chat_id, Linking.user_id == user_id).execute()
        except TelegramForbiddenError:
            Linking.delete().where(Linking.chat_id == link.chat_id).execute()
    return chats

async def is_linked(user_id: int, chat_id: int) -> Chat | None:
    chat: Chat | None = None
    try:
        chat = await bot.get_chat(chat_id)
        if not (Linking.select().where(Linking.user_id == user_id).where(Linking.chat_id == chat_id)):
            return None
        if await is_user_admin(user_id, chat) != 2:
            return None
    except TelegramForbiddenError:
        Linking.delete().where(Linking.chat_id == chat_id).execute()
    return chat

def unlink_chat_from_user(user_id: int, chat_id: int):
    Linking.delete().where(Linking.user_id==user_id, Linking.chat_id==chat_id).execute()

def add_schedule(chat_id: int, date: datetime, post: Post):
    Schedule.create(chat_id=chat_id, date=date, post=post.serialize())

def get_need_to_schedule(need_delete = False, chat_id: int | None = None):
    table: list[tuple[int, datetime, Post]] = []
    query = Schedule.select().where(Schedule.date <= datetime.now())
    if chat_id is not None:
        query = query.where(Schedule.chat_id == chat_id)
    for schedule in query:
        if need_delete:
            Schedule.delete().where(Schedule.id == schedule.id).execute()
        table.append((schedule.chat_id, schedule.date, Post.deserialize(schedule.post)))
    return table

def get_schedule(chat_id: int, offset: int) -> tuple[int, Post, datetime] | None:
    d = list(Schedule.select().where(Schedule.chat_id == chat_id).offset(offset - 1))
    if len(d) == 0:
        return None, None, None
    return d[0].id, Post.deserialize(d[0].post), d[0].date

def get_schedule_direct(schedule_id: int) -> tuple[int, Post, datetime] | None:
    d = list(Schedule.select().where(Schedule.id == schedule_id))
    if len(d) == 0:
        return None, None, None
    return d[0].id, Post.deserialize(d[0].post), d[0].date 

def delete_schedule(schedule_id: int):
    Schedule.delete().where(Schedule.id == schedule_id).execute()

def update_schedule(schedule_id: int, post: Post | None, date: datetime | None):
    if post is not None:
        Schedule.update(post=post.serialize()).where(Schedule.id == schedule_id).execute()
    if date is not None:
        Schedule.update(date=date).where(Schedule.id == schedule_id).execute()

def count_schedule(chat_id: int):
    return len(Schedule.select().where(Schedule.chat_id == chat_id))
