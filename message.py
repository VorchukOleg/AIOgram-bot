from globals import bot

class Post:
    text: str = ''
    photo: list[str] = []

    async def send(self, chat_id: int):
        if len(self.photo) == 1:
            await bot.send_photo(chat_id=chat_id, photo=self.photo[0], caption=self.text, parse_mode='markdown')
        else:
            await bot.send_message(chat_id=chat_id, text=self.text, parse_mode='markdown')