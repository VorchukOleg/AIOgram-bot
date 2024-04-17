import asyncio
import logging
import sys

from globals import *
import scheduler
import handlers

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    scheduler.run()
    asyncio.run(main())
    
