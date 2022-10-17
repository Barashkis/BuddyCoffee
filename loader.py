from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sql import Database

bot = Bot(token=config.token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database(path_to_db="main.db")
tz = 'Europe/Moscow'
scheduler = AsyncIOScheduler(timezone=tz)
