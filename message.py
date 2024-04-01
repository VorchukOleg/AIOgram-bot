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