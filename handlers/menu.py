from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from config import (
    applicant_menu,
    expert_menu,
)
from database import Expert
from keyboards import kb_from_mapping
from loader import (
    PostgresSession,
    dp,
)
from logger import logger


@dp.message_handler(Command('menu'))
async def menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with state.proxy() as data:
        role = data.get('role')

    if role:
        if role == 'a':
            await message.answer(
                'Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu',
                reply_markup=kb_from_mapping(applicant_menu),
            )
            logger.debug(f'Applicant {user_id} use /menu command')
        else:
            with PostgresSession.begin() as session:
                expert = session.query(Expert).get(user_id)

            if expert.status == 'На модерации':  # type: ignore
                await message.answer(
                    'Вы не можете использовать функционал бота, пока Ваша анкета находится на модерации'
                )
                logger.debug(f'Expert on moderation {user_id} use /menu command')
            else:
                await message.answer(
                    'Вы в главном меню. Если захотите сюда вернуться, используйте команду /menu',
                    reply_markup=kb_from_mapping(expert_menu),
                )
                logger.debug(f'Expert {user_id} use /menu command')
    else:
        await message.answer('Вы не зарегистрированы в боте. Чтобы зарегистрироваться, введите команду /start')
        logger.debug(f'Unregistered user {user_id} use /menu command')
