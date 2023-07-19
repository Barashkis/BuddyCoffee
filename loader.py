from aiogram import (
    Bot,
    Dispatcher,
    types,
)
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import sessionmaker

from config import (
    postgres_host,
    postgres_name,
    postgres_password,
    postgres_user,
    redis_password,
    token,
    tz,
)
from database import new_engine


__all__ = (
    'bot',
    'dp',
    'postgres_engine',
    'PostgresSession',
    'scheduler',
    'storage',
)

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(password=redis_password)
dp = Dispatcher(bot, storage=storage)

postgres_engine = new_engine(
        dialect='postgresql',
        driver='psycopg2',
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        name=postgres_name,
    )
PostgresSession = sessionmaker(bind=postgres_engine)

scheduler = AsyncIOScheduler(timezone=tz)
