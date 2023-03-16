import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Regexp
from aiogram.types import Message, CallbackQuery

from config import topics_list
from keyboards import kb2b, experts_to_confirm_kb2, kb3b, expert_menu_kb
from loader import dp, db, bot
from my_logger import logger


@dp.message_handler(Command("notify_all"))
async def notify_all(message: Message):
    user_id = message.from_user.id

    logger.debug(f'{user_id} entered /notify_all command')
    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if user_id in admin_ids:
            users = db.get_applicants() + db.get_experts()
            await message.answer(f'В базе всего {len(users)} пользователей.',
                                 reply_markup=kb2b("Написать сообщение", "admin_send_msg_all", "Назад", "close_keyboard"))
            logger.debug(f"Admin {user_id} entered notify_all handler")


@dp.message_handler(Command("notify_inactive"))
async def notify_inactive(message: Message):
    user_id = message.from_user.id

    logger.debug(f'{user_id} entered /notify_inactive command')
    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if user_id in admin_ids:
            inactive_users = db.get_inactive_applicants()
            await message.answer(f'В базе {len(inactive_users)} пользователей, которые ни разу '
                                 f'не инициировали встречу.',
                                 reply_markup=kb2b("Написать сообщение", "admin_send_msg_inactive", "Назад", "close_keyboard"))
            logger.debug(f"Admin {user_id} entered notify_inactive handler")


@dp.message_handler(Command("notify_applicants"))
async def notify_applicants(message: Message):
    user_id = message.from_user.id

    logger.debug(f'{user_id} entered /notify_applicants command')
    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if user_id in admin_ids:
            applicants = db.get_applicants()
            await message.answer(f'В базе всего {len(applicants)} соискателей',
                                 reply_markup=kb2b("Написать сообщение", "admin_send_msg_applicants", "Назад", "close_keyboard"))
            logger.debug(f"Admin {user_id} entered notify_applicants handler")


@dp.callback_query_handler(Regexp(r'^admin_send_msg_'))
async def send_msg_to_users(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer(f"Напишите сообщение, которое будет отправлено пользователям.")
    cd = call.data
    notify_type = cd[15:]
    await state.set_state('admin_confirm_msg')
    async with state.proxy() as data:
        data["notify_type"] = notify_type
    logger.debug(f"Admin {call.from_user.id} entered send_msg_to_{notify_type}_users handler")


@dp.message_handler(state='admin_confirm_msg')
async def confirm_message_sending(message: Message, state: FSMContext):
    data = await state.get_data()
    notify_type = data["notify_type"]
    await state.finish()

    text = message.text
    async with state.proxy() as data:
        data["message_text"] = text

    await message.answer("Сообщение, которое Вы хотите разослать, будет выглядеть вот так:\n\n"
                         f"{text}\n\n"
                         "Вы подтверждаете отправку этого сообщения?",
                         reply_markup=kb2b("Подтверждаю", f"admin_write_msg_{notify_type}", "Отменить отправку", "close_keyboard"))
    logger.debug(f"Admin {message.from_user.id} entered confirm_message_sending handler")


@dp.callback_query_handler(text='admin_write_msg_all')
async def send_msg_to_all_users(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    status_message = (await bot.send_message(call.from_user.id, "Производится рассылка сообщения..."))

    data = await state.get_data()
    message_text = data["message_text"]

    users = db.get_applicants() + db.get_experts()
    for user in users:
        try:
            await bot.send_message(user[0], text=message_text)
            await asyncio.sleep(.05)
        except Exception as e:
            logger.debug(e)
    await status_message.edit_text(f'Ваше сообщение было отправлено {len(users)} пользователям')
    logger.debug(f"Admin {call.from_user.id} send notification to all users")


@dp.callback_query_handler(text='admin_write_msg_inactive')
async def send_msg_to_inactive_users(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    status_message = (await bot.send_message(call.from_user.id, "Производится рассылка сообщения..."))

    data = await state.get_data()
    message_text = data["message_text"]

    inactive_users = db.get_inactive_applicants()
    for applicant in inactive_users:
        try:
            await bot.send_message(applicant[0], text=message_text)
            await asyncio.sleep(.05)
        except Exception as e:
            logger.debug(e)
    await status_message.edit_text(f'Ваше сообщение было отправлено {len(inactive_users)} пользователям')
    logger.debug(f"Admin {call.from_user.id} send notification to inactive users")


@dp.callback_query_handler(text='admin_write_msg_applicants')
async def send_msg_to_applicants(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    status_message = (await bot.send_message(call.from_user.id, "Производится рассылка сообщения..."))

    data = await state.get_data()
    message_text = data["message_text"]

    applicants = db.get_applicants()
    for applicant in applicants:
        try:
            await bot.send_message(applicant[0], text=message_text)
            await asyncio.sleep(.05)
        except Exception as e:
            logger.debug(e)
    await status_message.edit_text(f'Ваше сообщение было отправлено {len(applicants)} соискателям')
    logger.debug(f"Admin {call.from_user.id} send notification to applicants")


@dp.message_handler(Command("add_admin"))
async def add_admin(message: Message):
    user_id = message.from_user.id

    logger.debug(f'{user_id} entered /add_admin command')
    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if user_id in admin_ids:
            await message.answer(f'Вы собираетесь добавить нового модератора. Нажмите кнопку "Добавить", если хотите '
                                 f'это сделать',
                                 reply_markup=kb2b("Добавить", "add_admin", "Назад", "close_keyboard"))
            logger.debug(f"Admin {user_id} entered add_admin handler")


@dp.callback_query_handler(text='add_admin')
async def adding_admin(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"Перешлите в бота любое сообщение пользователя, которого хотите сделать модератором")
    await state.set_state('adding_admin')
    logger.debug(f"Admin {call.from_user.id} entered adding_admin handler")


@dp.message_handler(state='adding_admin')
async def proceed_adding_admin(message: Message, state: FSMContext):
    try:
        new_admin = message.forward_from.id
        db.add_admin(new_admin)
        await message.answer("Пользователь был добавлен в список модераторов бота")
        await state.finish()
        logger.debug(f"Admin {message.from_user.id} added new admin to bot: {new_admin}")
    except Exception as e:
        await message.answer("Что-то пошло не так, бот не смог добавить нового пользователя в список модераторов")
        await state.finish()
        logger.warning(f"Admin {message.from_user.id} tried to add new admin to bot but cause an error: {e}")


@dp.message_handler(Command("stats"))
async def show_stats(message: Message):
    user_id = message.from_user.id

    logger.debug(f'{user_id} entered /stats command')

    admin_ids_raw = db.get_admins()
    if admin_ids_raw is not None:
        admin_ids = []
        for t in admin_ids_raw:
            admin_ids.append(t[0])
        if user_id in admin_ids:
            stats = db.get_stats()
            await message.answer(
                f'В базе {stats[0][1]} экспертов и {stats[1][1]} соискателей, нажавших на кнопку "Показать контакты"')

            logger.debug(f"Admin {user_id} entered show_stats handler")


@dp.message_handler(Command("moderation"))
async def moderation(message: Message):
    experts_to_confirm = db.get_experts_to_confirm()
    if experts_to_confirm:
        ed = experts_to_confirm[0]

        if ed[7]:
            division = ed[7]
        else:
            division = ed[8]

        if ed[2]:
            username = f"@{ed[2]}"
        else:
            username = f"@{ed[13]}"

        topics = ", ".join([topics_list[int(topic_id)] for topic_id in ed[12].split(", ")])

        text = f"<b>Имя:</b> {ed[5]}\n" \
               f"<b>Имя в Telegram:</b> {username}\n" \
               f"<b>Направление:</b> {ed[6]}\n" \
               f"<b>Дивизион:</b> {division}\n" \
               f"<b>Темы для разговора:</b> {topics}\n" \
               f"<b>Экспертный профиль:</b> {ed[10]}\n"

        if ed[15]:
            if len(text) <= 1024:
                await message.answer_photo(ed[15],
                                           caption=text,
                                           reply_markup=experts_to_confirm_kb2(experts_to_confirm),
                                           disable_notification=True)
            else:
                await message.answer_photo(ed[15])
                await message.answer(text,
                                     reply_markup=experts_to_confirm_kb2(experts_to_confirm),
                                     disable_notification=True)
        else:
            await message.answer(text=text,
                                 reply_markup=experts_to_confirm_kb2(experts_to_confirm),
                                 disable_notification=True)
    else:
        await message.answer("Пока нету экспертов, подавших заявку на модерацию")

    logger.debug(f"Admin {message.from_user.id} entered moderation handler")


@dp.callback_query_handler(text='close_keyboard')
async def close_keyboard(call: CallbackQuery):
    await call.message.delete()

    logger.debug(f"Admin {call.message.from_user.id} entered close_keyboard handler")


@dp.callback_query_handler(Regexp(r'^admin_sekbp_'))
async def page_click_expert_to_confirm(call: CallbackQuery):
    await call.message.delete()

    page = int(call.data[12:])
    experts_to_confirm = db.get_experts_to_confirm()

    if experts_to_confirm:
        ed = experts_to_confirm[page - 1]

        if ed[7]:
            division = ed[7]
        else:
            division = ed[8]

        if ed[2]:
            username = f"@{ed[2]}"
        else:
            username = f"@{ed[13]}"

        topics = ", ".join([topics_list[int(topic_id)] for topic_id in ed[12].split(", ")])

        text = f"<b>Имя:</b> {ed[5]}\n" \
               f"<b>Имя в Telegram:</b> {username}\n" \
               f"<b>Направление:</b> {ed[6]}\n" \
               f"<b>Дивизион:</b> {division}\n" \
               f"<b>Темы для разговора: {topics}</b>\n" \
               f"<b>Экспертный профиль:</b> {ed[10]}\n"

        if ed[15]:
            if len(text) <= 1024:
                await call.message.answer_photo(ed[15],
                                                caption=text,
                                                reply_markup=experts_to_confirm_kb2(experts_to_confirm, page),
                                                disable_notification=True)
            else:
                await call.message.answer_photo(ed[15])
                await call.message.answer(text,
                                          reply_markup=experts_to_confirm_kb2(experts_to_confirm, page),
                                          disable_notification=True)
        else:
            await call.message.answer(text=text,
                                      reply_markup=experts_to_confirm_kb2(experts_to_confirm, page),
                                      disable_notification=True)
    else:
        await call.message.answer("Пока нету экспертов, подавших заявку на модерацию")

    logger.debug(f"Admin {call.from_user.id} entered page_click_expert_to_confirm handler with page {page}")


@dp.callback_query_handler(Regexp(r'^admin_choosee_'))
async def expert_to_confirm_chosen(call: CallbackQuery):
    expert_id = int(call.data[14:])
    await call.message.edit_reply_markup(reply_markup=kb3b("Утвердить", f"confirm_expert_{expert_id}",
                                                           "Отклонить", f"deny_expert_{expert_id}",
                                                           "Назад", "back_to_pagination"))

    logger.debug(f"Admin {call.from_user.id} entered expert_to_confirm_chosen handler "
                 f"with expert {expert_id}")


@dp.callback_query_handler(text='back_to_pagination')
async def back_to_pagination(call: CallbackQuery):
    experts_to_confirm = db.get_experts_to_confirm()
    await call.message.edit_reply_markup(experts_to_confirm_kb2(experts_to_confirm))

    logger.debug(f"Admin {call.from_user.id} entered back_to_pagination handler")


@dp.callback_query_handler(Regexp(r'^confirm_expert_'))
async def confirm_expert(call: CallbackQuery):
    await call.message.edit_reply_markup()

    expert_id = int(call.data[15:])
    expert = db.get_expert(expert_id)
    if expert[14] == "На модерации":
        await bot.send_message(chat_id=expert_id,
                               text="Поздравляем! Ваша анкета прошла модерацию",
                               disable_notification=True)
        await bot.send_message(chat_id=expert_id,
                               text="Выберите подходящий пункт",
                               reply_markup=expert_menu_kb,
                               disable_notification=True)
        db.update_user('experts', 'status', expert_id, None)

        await call.message.answer("Доступ к функционалу эксперта был успешно предоставлен данному пользователю")
    else:
        await call.message.answer("Кто-то из других админов уже обработал данную анкету")

    logger.debug(f"Admin {call.from_user.id} entered confirm_expert handler "
                 f"with expert {expert_id}")


@dp.callback_query_handler(Regexp(r'^deny_expert_'))
async def confirm_expert(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Функционал эксперта не был предоставлен данному пользователю")

    expert_id = int(call.data[12:])
    await bot.send_message(chat_id=expert_id,
                           text="К сожалению, Ваша анкета не прошла модерацию. "
                                "Чтобы повторно пройти регистрацию, воспользуйтесь командой /start",
                           disable_notification=True)
    db.delete_user('experts', expert_id)

    logger.debug(f"Admin {call.from_user.id} entered deny_expert handler "
                 f"with expert {expert_id}")
