from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery
from handlers.utils import build_applicant_menu_message_text
from keyboards import kb1b, applicant_menu_kb, expert_menu_kb, kb2b
from loader import dp, db
from my_logger import logger
from aiogram.utils.deep_linking import decode_payload


@dp.message_handler(Command("menu"))
async def start(message: Message):
    user_id = message.from_user.id

    user_expert = db.get_expert(user_id)
    user_applicant = db.get_applicant(user_id)

    if user_applicant:
        await message.answer(
            text=build_applicant_menu_message_text(),
            reply_markup=applicant_menu_kb,
            disable_notification=True,
        )
        logger.debug(f'Applicant {user_id} use /menu command')
    elif user_expert:
        if user_expert[14] != "На модерации":
            await message.answer(text="Вы в главном меню. Если захотите сюда вернуться, используйте команду /menu",
                                 reply_markup=expert_menu_kb,
                                 disable_notification=True)
            logger.debug(f'Expert {user_id} use /menu command')
        else:
            await message.answer("Вы не можете использовать функционал бота, пока Ваша анкета находится на модерации")

            logger.debug(f'Expert on moderation {user_id} use /menu command')
    else:
        await message.answer("Вы не зарегистрированы в боте. Чтобы зарегистрироваться, введите команду /start")

        logger.debug(f'User {user_id} use /menu command')


@dp.message_handler(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id

    args = message.get_args()
    if args:
        try:
            payload = decode_payload(args)
            if payload == 'expert':
                await message.answer(text="Добрый день! Для начала работы в боте и организации "
                                          "встреч с соискателями вам нужно зарегистрироваться.",
                                     reply_markup=kb1b("Заполнить анкету 🖋️", "expert_start"))
                logger.debug(f'User {user_id} start the bot as an expert')
        except Exception as e:
            await message.answer(text="Кажется, вы уже регистрировались в боте. "
                                      "Если хотите изменить свой профиль, воспользуйтесь командой /menu")
            logger.warning(f'User {user_id} entered bot with unknown start args: {args}, '
                           f'and got exception: {e}')
    else:
        is_expert = db.get_expert(user_id) is not None
        is_applicant = db.get_applicant(user_id) is not None
        if not is_applicant and not is_expert:
            await message.answer(text="Добрый день! Пожалуйста, скажите, кто вы:",
                                 reply_markup=kb2b("Я соискатель (школьник или студент)", "applicant_start",
                                                   "Я эксперт", "warn_expert_registration"))
            logger.debug(f'User {user_id} start bot')
        else:
            await message.answer(text="Кажется, вы уже регистрировались в боте. "
                                      "Если хотите изменить свой профиль, воспользуйтесь командой /menu")
            logger.debug(f'User {user_id} tried to use /start command again')


@dp.callback_query_handler(text='warn_expert_registration')
async def back_to_the_choice(call: CallbackQuery):
    await call.answer(cache_time=5)
    await call.message.answer(text="Убедитесь, что вы не ошиблись с выбором роли. Эксперт — сотрудник Росатома, "
                                   "который проводит консультации. Соискатель ещё не работает в Росатоме. "
                                   "Если вы ошиблись ролью, вы можете вернуться назад, нажав на соответствующую кнопку",
                              reply_markup=kb2b("Вернуться к выбору роли", "back_to_the_choice",
                                                "Продолжить", "expert_start"),
                              disable_notification=True)
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text='back_to_the_choice')
async def back_to_the_choice(call: CallbackQuery):
    await call.message.edit_text(text="Добрый день! Пожалуйста, скажите, кто вы:",
                                 reply_markup=kb2b("Я соискатель (школьник или студент)", "applicant_start",
                                                   "Я эксперт", "warn_expert_registration"))
