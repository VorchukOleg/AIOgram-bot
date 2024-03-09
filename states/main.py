from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from statemanager import State



class Main(State):
    async def on_init(self):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text='✌️ Пинг', callback_data='ping')
        await self.bot.send_message(self.chat_id, '💻 Привет, главное меню', reply_markup=keyboard.as_markup())
    
    async def on_callback(self, query: CallbackQuery):
        if query.data == 'ping':
            await self.bot.send_message(text='🤞 Понг', chat_id=self.chat_id)
            await query.answer()