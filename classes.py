from globals import bot
from aiogram import Bot
from aiogram.types import InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

class Post:
    text: str = ''
    photo: list[str] = []
    buttons: list[list[tuple[str, str]]] = []

    async def send(self, chat_id: int, bot: Bot = bot):
        keyboard = InlineKeyboardBuilder()
        for row in self.buttons:
            keyboard = keyboard.row(*[InlineKeyboardButton(text=x[0], url=x[1]) for x in row])
        if len(self.photo) == 1:
            await bot.send_photo(chat_id=chat_id, photo=self.photo[0], caption=self.text, parse_mode='markdown', reply_markup=keyboard.as_markup())
        elif len(self.photo) > 1:
            media = [InputMediaPhoto(media=x) for x in self.photo]
            media[0].caption = self.text
            messages = await bot.send_media_group(chat_id, media)
            messages[0].edit_reply_markup(reply_markup=keyboard.as_markup())
        else:
            await bot.send_message(chat_id=chat_id, text=self.text, parse_mode='markdown', reply_markup=keyboard.as_markup())
    
    def is_empty(self):
        return self.text == '' and len(self.photo) == 0
    
    def serialize(self):
        return json.dumps({
            'text': self.text,
            'photo': self.photo,
            'buttons': self.buttons,
        })

    @staticmethod
    def deserialize(jsn: str):
        values = json.loads(jsn)
        post = Post()
        post.text = values['text']
        post.photo = values['photo']
        post.buttons = values['buttons']
        return post

    def __str__(self) -> str:
        return f'({self.text or 'None'}, {self.photo}, {self.buttons})'
    
    def __repr__(self) -> str:
        return self.__str__()

class State:
    status: str 
    chat_id: int | None = None
    post: Post | None = None

    def __init__(self, status: str = '', chat_id: int | None = None, post: Post | None = None):
        self.status = status
        self.chat_id = chat_id
        self.post = post

    def __str__(self) -> str:
        return f'({self.status}, {self.chat_id or 'None'}, {self.post or 'None'})'