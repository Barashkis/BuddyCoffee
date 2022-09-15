from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from keyboards import kb1b, applicant_menu_kb, expert_menu_kb, kb2b
from loader import dp, db
from my_logger import logger
from aiogram.utils.deep_linking import decode_payload


# @dp.message_handler(Command("start"))
# async def start(message: Message):
#     args = message.get_args()
#     date = message.date.strftime('%d.%m.%Y %H:%M')
#     if args:
#         try:
#             payload = decode_payload(args)
#             if payload == 'expert':
#                 db.add_expert(message.from_user.id, date, message.from_user.username, message.from_user.first_name,
#                               message.from_user.last_name)
#                 await message.answer(text="Добрый день! Для начала работы в боте и организации "
#                                           "встреч с соискателями вам нужно зарегистрироваться.",
#                                      reply_markup=kb1b("Заполнить анкету 🖋️", "expert_start"))
#                 logger.debug(f'User {message.from_user.id} start the bot as an expert')
#         except Exception as e:
#             await message.answer(text="Кажется, вы уже регистрировались в боте. "
#                                       "Если хотите изменить свой профиль, воспользуйтесь командой /menu")
#             logger.warning(f'User {message.from_user.id} entered bot with unknown start args: {args}, '
#                          f'and got exception: {e}')
#     else:
#         if db.get_expert(message.from_user.id) is None:
#             db.add_applicant(message.from_user.id, date, message.from_user.username, message.from_user.first_name,
#                              message.from_user.last_name)
#             await message.answer(text="Добрый день! Для начала работы в боте и организации "
#                                       "встреч с экспертами тебе нужно зарегистрироваться.",
#                                  reply_markup=kb1b("Заполнить анкету 🖋️", "applicant_start"))
#             logger.debug(f'User {message.from_user.id} start the bot as an applicant')
#         else:
#             await message.answer(text="Кажется, вы уже регистрировались в боте. "
#                                       "Если хотите изменить свой профиль, воспользуйтесь командой /menu")
#             logger.debug(f'User {message.from_user.id} tried to use /start command again')


@dp.message_handler(Command("menu"))
async def start(message: Message):
    if db.get_expert(message.from_user.id) is None:
        await message.answer(text="Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu",
                             reply_markup=applicant_menu_kb,
                             disable_notification=True)
        logger.debug(f'Applicant {message.from_user.id} use /menu command')
    else:
        await message.answer(text="Вы в главном меню. Если захотите сюда вернуться, используйте команду /menu",
                             reply_markup=expert_menu_kb,
                             disable_notification=True)
        logger.debug(f'Expert {message.from_user.id} use /menu command')


@dp.message_handler(Command("start"))
async def start(message: Message):
    args = message.get_args()
    date = message.date.strftime('%d.%m.%Y %H:%M')
    if args:
        try:
            payload = decode_payload(args)
            if payload == 'expert':
                await message.answer(text="Добрый день! Для начала работы в боте и организации "
                                          "встреч с соискателями вам нужно зарегистрироваться.",
                                     reply_markup=kb1b("Заполнить анкету 🖋️", "expert_start"))
                logger.debug(f'User {message.from_user.id} start the bot as an expert')
        except Exception as e:
            await message.answer(text="Кажется, вы уже регистрировались в боте. "
                                      "Если хотите изменить свой профиль, воспользуйтесь командой /menu")
            logger.warning(f'User {message.from_user.id} entered bot with unknown start args: {args}, '
                         f'and got exception: {e}')
    else:
        if db.get_expert(message.from_user.id) is None and db.get_applicant(message.from_user.id) is None:
            await message.answer(text="Добрый день! Пожалуйста, скажите, кто вы:",
                                 reply_markup=kb2b("Я соискатель", "applicant_start", "Я эксперт", "expert_start"))
            logger.debug(f'User {message.from_user.id} start bot')
        else:
            await message.answer(text="Кажется, вы уже регистрировались в боте. "
                                      "Если хотите изменить свой профиль, воспользуйтесь командой /menu")
            logger.debug(f'User {message.from_user.id} tried to use /start command again')