from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message, Chat, CallbackQuery

class State:
    __stateManager: StateManager

    async def init(self, stateManager: StateManager):
        self.__stateManager = stateManager
        await self.on_init()

    @property
    def stateManager(self) -> StateManager:
        return self.__stateManager
    
    @property
    def bot(self) -> Bot:
        return self.__stateManager.bot

    @property
    def chat_id(self) -> int:
        return self.__stateManager.chat_id(self)

    async def chat(self) -> Chat:
        return await self.__stateManager.get_chat(self)

    async def on_init(self):
        pass

    async def on_callback(self, query: CallbackQuery):
        pass

    async def on_message(self, message: Message):
        pass

class StateManager:
    __states: dict[int, State] = {}
    __bot: Bot

    def __init__(self, bot: Bot):
        self.__bot = bot

    async def set_state(self, chat_id: int, state: State):
        self.__states[chat_id] = state
        await self.__states[chat_id].init(self)

    def chat_id(self, state: State) -> int:
        states = list(filter(lambda x: self.__states[x] == state, self.__states))
        if len(states) == 0:
            return None
        return states[0]

    async def get_chat(self, state: State) -> Chat:
        chat_id = self.chat_id(state)
        if chat_id != None:
            return await self.__bot.get_chat(self.chat_id(state))
        return None

    def state(self, chat_id: int) -> State:
        states = list(filter(lambda x: x == chat_id, self.__states))
        if len(states) == 0:
            return None
        return self.__states[states[0]]

    @property
    def bot(self):
        return self.__bot