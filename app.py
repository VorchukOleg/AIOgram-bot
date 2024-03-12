from aiogram import Dispatcher, Bot

from config import TELEGRAM_TOKEN
from statemanager import StateManager

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher()
sm = StateManager(bot)
