import asyncio
from threading import Thread
from database import get_need_to_schedule
from config import TELEGRAM_TOKEN
from aiogram import Bot

bot = Bot(TELEGRAM_TOKEN)

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def loop_func():
    while True:
        for x in get_need_to_schedule(True):
            await x[2].send(x[0], bot)
        await asyncio.sleep(10)

def run():
    loop = asyncio.new_event_loop()
    t = Thread(target=start_background_loop, args=(loop,), daemon=True)
    t.start()

    asyncio.run_coroutine_threadsafe(loop_func(), loop)