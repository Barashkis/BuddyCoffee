import sqlalchemy
from aiogram import executor
from bot_commands import set_default_commands
from loader import bot, dp, storage, db, scheduler
from my_logger import logger
from config import directions_list, divisions_list
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

    experts = db.get_experts()
    for expert in experts:
        if str(expert[6]).isdigit():
            db.update_user('experts', 'direction', expert[0], directions_list[int(expert[6])])

        if str(expert[7]).isdigit():
            db.update_user('experts', 'division', expert[0], divisions_list[int(expert[7])])

    applicants = db.get_applicants()
    for applicant in applicants:
        if str(applicant[7]).isdigit():
            db.update_user('applicants', 'direction', applicant[0], directions_list[int(applicant[7])])

    try:
        db.add_new_column("meetings", "api_id", "BIGINT")
        logger.info('Column "api_id" is added to the "meetings" table')
    except Exception as e:
        logger.info(e)

    try:
        db.add_new_column("applicants", "last_activity", "TEXT")
        logger.info('Column "last_activity" is added to the "applicants" table')
    except Exception as e:
        logger.info(e)

    try:
        db.add_new_column("experts", "last_activity", "TEXT")
        logger.info('Column "last_activity" is added to the "experts" table')
    except Exception as e:
        logger.info(e)

    try:
        db.add_new_column("meetings", "rating", "INTEGER")
        logger.info('Column "rating" is added to the "meetings" table')
    except Exception as e:
        logger.info(e)

    try:
        db.add_new_column("experts", "rating", "REAL")
        logger.info('Column "rating" is added to the "experts" table')
    except Exception as e:
        logger.info(e)

    try:
        db.add_new_column("experts", "agree_to_show_contacts", "INTEGER")
        logger.info('Column "agree_to_show_contacts" is added to the "experts" table')
    except Exception as e:
        logger.info(e)

    try:
        db.add_new_column("applicants", "agree_to_show_contacts", "INTEGER")
        logger.info('Column "agree_to_show_contacts" is added to the "applicants" table')
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
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)
