import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards import kb2b, applicant_menu_kb
from loader import dp, db, bot
from my_logger import logger


@dp.message_handler(Command("notify"))
async def notify(message: Message):
    logger.debug(f'{message.from_user.id} entered /notify command')
    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if message.from_user.id in admin_ids:
            inactive_users = db.get_inactive_applicants()
            await message.answer(f'В базе {len(inactive_users)} пользователей, которые ни разу '
                                 f'не инициировали встречу.',
                                 reply_markup=kb2b("Написать сообщение", "admin_send_msg", "Назад", "applicant_menu"))
            logger.debug(f"Admin {message.from_user.id} entered notify handler")


@dp.callback_query_handler(text='admin_send_msg')
async def send_msg_to_inactive_users(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"Напишите сообщение, которое будет отправлено пользьзователям.")
    await state.set_state('admin_write_msg')
    logger.debug(f"Admin {call.from_user.id} entered send_msg_to_inactive_users handler")


@dp.message_handler(state='admin_write_msg')
async def send_msg_to_inactive_users(message: Message, state: FSMContext):
    msg = message.text
    inactive_users = db.get_inactive_applicants()
    for applicant in inactive_users:
        try:
            await bot.send_message(applicant[0], text=f"{msg}")
            await asyncio.sleep(.05)
        except Exception as e:
            logger.debug(e)
    await message.answer(f'Ваше сообщение было отправлено {len(inactive_users)} пользователям',
                         reply_markup=applicant_menu_kb)
    await state.finish()
    logger.debug(f"Admin {message.from_user.id} send notification to inactive users")


@dp.message_handler(Command("add_admin"))
async def add_admin(message: Message, state: FSMContext):
    logger.debug(f'{message.from_user.id} entered /add_admin command')
    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if message.from_user.id in admin_ids:
            await message.answer(f'Вы собираетесь добавить нового модератора. Нажмите кнопку "Добавить", если хотите '
                                 f'это сделать',
                                 reply_markup=kb2b("Добавить", "add_admin", "Назад", "applicant_menu"))
            logger.debug(f"Admin {message.from_user.id} entered add_admin handler")

@dp.callback_query_handler(text='add_admin')
async def adding_admin(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"Перешлите в бота любое сообщение пользователя, которого хотите сделать модератором")
    await state.set_state('adding_admin')
    logger.debug(f"Admin {call.from_user.id} entered adding_admin handler")


@dp.message_handler(state='adding_admin')
async def send_msg_to_inactive_users(message: Message, state: FSMContext):
    try:
        new_admin = message.forward_from.id
        db.add_admin(new_admin)
        await message.answer("Пользователь был добавлен в список модераторов бота",
                             reply_markup=applicant_menu_kb)
        await state.finish()
        logger.debug(f"Admin {message.from_user.id} added new admin to bot: {new_admin}")
    except Exception as e:
        await message.answer("Что-то пошло не так, бот не смог добавить нового пользователя в список модераторов",
                             reply_markup=applicant_menu_kb)
        await state.finish()
        logger.warning(f"Admin {message.from_user.id} tried to add new admin to bot but cause an error: {e}")


@dp.message_handler(Command("stats"))
async def show_stats(message: Message):
    logger.debug(f'{message.from_user.id} entered /stats command')

    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if message.from_user.id in admin_ids:
            stats = db.get_stats()
            await message.answer(f'В базе {stats[0][1]} экспертов и {stats[1][1]} соискателей, нажавших на кнопку "Показать контакты"',
                                 reply_markup=applicant_menu_kb)

            logger.debug(f"Admin {message.from_user.id} entered show_stats handler")
