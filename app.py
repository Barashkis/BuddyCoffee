import sqlalchemy
from aiogram import executor
from bot_commands import set_default_commands
from loader import bot, dp, storage, db, scheduler
from my_logger import logger
import handlers


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    try:
        db.cr_table_applicants()
        logger.info('Table "applicants" is created')
    except Exception as e:
        logger.info(e)
    try:
        db.cr_table_experts()
        logger.info('Table "experts" is created')
    except Exception as e:
        logger.info(e)
    try:
        db.cr_table_meetings()
        logger.info('Table "meetings" is created')
    except Exception as e:
        logger.info(e)
    try:
        db.cr_table_admins()
        logger.info('Table "admins" is created')
    except Exception as e:
        logger.info(e)
    try:
        db.cr_table_stats()
        db.add_initial_stats()
        logger.info('Table "stats" is created')
    except Exception as e:
        logger.info(e)
    try:
        db.cr_table_local_contacts()
        logger.info('Table "local_contacts" is created')
    except Exception as e:
        logger.info(e)
    logger.info('Bot is running')


async def on_shutdown(dispatcher):
    await bot.close()
    await storage.close()
    scheduler.shutdown()
    logger.info("Bot stopped")


if __name__ == '__main__':
    scheduler.add_jobstore('sqlalchemy', url='sqlite:///main.db')
    scheduler.start()
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup, skip_updates=True)
