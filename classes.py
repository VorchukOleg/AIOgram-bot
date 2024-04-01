from globals import bot
from aiogram.types import InputMediaPhoto

class Post:
    text: str = ''
    photo: list[str] = []

    async def send(self, chat_id: int):
        if len(self.photo) == 1:
            await bot.send_photo(chat_id=chat_id, photo=self.photo[0], caption=self.text, parse_mode='markdown')
        elif len(self.photo) > 1:
            media = [InputMediaPhoto(media=x) for x in self.photo]
            media[0].caption = self.text
            await bot.send_media_group(chat_id, media)
        else:
            await bot.send_message(chat_id=chat_id, text=self.text, parse_mode='markdown')
    
    def is_empty(self):
        return self.text == '' and len(self.photo) == 0

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