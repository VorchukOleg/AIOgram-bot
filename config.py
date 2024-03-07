# Данный файл занимается загрузком конфигурационных/параметров бота
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
