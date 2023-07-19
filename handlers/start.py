from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.utils.deep_linking import decode_payload

from keyboards import (
    base_cd,
    kb_from_mapping,
)
from loader import dp
from logger import logger


@dp.message_handler(Command('start'))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with state.proxy() as data:
        role = data.get('role')

    if role:
        await message.answer(
            'Кажется, вы уже регистрировались в боте. Если хотите изменить свой профиль, воспользуйтесь командой /menu'
        )
        logger.debug(f'User {user_id} try to use /start command again')

    if args := message.get_args():
        if decode_payload(args) == 'expert':
            await message.answer(
                'Добрый день! Для начала работы в боте и организации '
                'встреч с соискателями вам нужно зарегистрироваться.',
                reply_markup=kb_from_mapping({'expert_start': 'Заполнить анкету 🖋️'}),
            )
            logger.debug(f'User {user_id} start the bot as an expert')

            return

    await message.answer(
        'Добрый день! Пожалуйста, скажите, кто вы',
        reply_markup=kb_from_mapping(
            {
                'applicant_start': 'Я соискатель (школьник или студент)',
                'warn_expert_registration': 'Я эксперт'
            }
        ),
    )
    logger.debug(f'User {user_id} start bot')


@dp.callback_query_handler(base_cd.filter(value='warn_expert_registration'))
async def warn_expert_registration(call: CallbackQuery):
    await call.message.edit_text(
        'Убедитесь, что вы не ошиблись с выбором роли. Эксперт — сотрудник Росатома, '
        'который проводит консультации. Соискатель ещё не работает в Росатоме. '
        'Если вы ошиблись ролью, вы можете вернуться назад, нажав на соответствующую кнопку',
        reply_markup=kb_from_mapping(
            {
                'back_to_the_choice': 'Вернуться к выбору роли',
                'expert_start': 'Продолжить'
            }
        ),
    )
    logger.debug(f'User {call.from_user.id} enter warn_expert_registration handler')


@dp.callback_query_handler(base_cd.filter(value='back_to_the_choice'))
async def back_to_the_choice(call: CallbackQuery):
    await call.message.edit_text(
        'Добрый день! Пожалуйста, скажите, кто вы',
        reply_markup=kb_from_mapping(
            {
                'applicant_start': 'Я соискатель (школьник или студент)',
                'warn_expert_registration': 'Я эксперт',
            }
        ),
    )
    logger.debug(f'User {call.from_user.id} enter back_to_the_choice handler')
