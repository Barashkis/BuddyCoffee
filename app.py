from aiogram import (
    Dispatcher,
    executor,
)

from commands import set_default_commands
from config import (
    postgres_host,
    postgres_name,
    postgres_password,
    postgres_user,
)
from database import PostgresBase
from handlers import dp
from loader import (
    PostgresSession,
    bot,
    postgres_engine,
    scheduler,
    storage,
)
from logger import logger
from migrations import run_migrations


async def on_startup(dp: Dispatcher):
    import middlewares

    await set_default_commands(dp)

    PostgresBase.metadata.create_all(postgres_engine)
    run_migrations(PostgresSession, 'postgres')

    middlewares.setup(dp)

    logger.info('Bot is running')


async def on_shutdown(_):
    await bot.close()
    await storage.close()
    scheduler.shutdown()

    logger.info("Bot stopped")


if __name__ == '__main__':
    scheduler.add_jobstore(
        'sqlalchemy',
        url=f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:5432/{postgres_name}'
    )
    scheduler.start()

    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)
