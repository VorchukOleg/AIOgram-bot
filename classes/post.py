from globals import bot
from aiogram import Bot
from aiogram.types import InputMediaPhoto, InlineKeyboardButton, InputMediaDocument, InputMediaVideo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .exceptions import CantBeMixed
import json

class Post:
    text: str
    media: list[tuple[str, str]]
    buttons: list[list[tuple[str, str]]]

    def __init__(self) -> None:
        self.text = ''
        self.media = []
        self.buttons = []

    async def send(self, chat_id: int, bot: Bot = bot, buttons: InlineKeyboardBuilder | None = None):
        keyboard = InlineKeyboardBuilder()
        for row in self.buttons:
            keyboard = keyboard.row(*[InlineKeyboardButton(text=x[0], url=x[1]) for x in row])
        if buttons is not None:
            keyboard = keyboard.attach(buttons)
        if len(self.media) == 1:
            if self.media[0][0] == 'photo':
                return await bot.send_photo(chat_id=chat_id, photo=self.media[0][1], caption=self.text, parse_mode='html', reply_markup=keyboard.as_markup())
            elif self.media[0][0] == 'document':
                return await bot.send_document(chat_id=chat_id, document=self.media[0][1], caption=self.text, parse_mode='html', reply_markup=keyboard.as_markup())
            elif self.media[0][0] == 'video':
                return await bot.send_video(chat_id=chat_id, video=self.media[0][1], caption=self.text, parse_mode='html', reply_markup=keyboard.as_markup())
        elif len(self.media) > 1:
            media = []
            for x in self.media:
                xt = None
                if x[0] == 'photo':
                    xt = InputMediaPhoto(media=x[1])
                elif x[0] == 'document':
                    xt = InputMediaDocument(media=x[1])
                elif x[0] == 'video':
                    xt = InputMediaVideo(media=x[1])
                if xt is not None:
                    media.append(xt)
            media[0].caption = self.text
            return await bot.send_media_group(chat_id, media)
        else:
            return await bot.send_message(chat_id=chat_id, text=self.text, parse_mode='html', reply_markup=keyboard.as_markup())
    
    def add_media(self, media: tuple[str, str]):
        for x in self.media:
            if x[0] != media[0]:
                raise CantBeMixed()
        self.media.append(media)

    def set_media(self, media: tuple[str, str]):
        self.media = [media]
    
    def is_empty(self):
        return self.text == '' and len(self.media) == 0
    
    def serialize(self):
        return json.dumps({
            'text': self.text,
            'media': self.media,
            'buttons': self.buttons,
        })

    @staticmethod
    def deserialize(jsn: str):
        values = json.loads(jsn)
        post = Post()
        post.text = values['text']
        post.media = values['media']
        post.buttons = values['buttons']
        return post

    def __str__(self) -> str:
        return f'({self.text or 'None'}, {self.media}, {self.buttons})'
    
    def __repr__(self) -> str:
        return self.__str__()
