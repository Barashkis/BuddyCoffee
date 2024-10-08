from datetime import datetime, timedelta

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import Message, CallbackQuery
from pytz import timezone

from handlers.notifications import notif_cancel_to_applicant, notif_1day, \
    notif_3hours, notif_cancel_to_applicant2, notif_after_show_contacts, notif_1hour, notif_5min, \
    feedback_notif_applicant, feedback_notif_expert, notif_cancel_to_applicant3
from handlers.utils import track_user_activity
from keyboards import expert_menu_kb, kb1b, kb3b, suitable_applicants_kb2, kb2b, meetings_e_kb, \
    slots_kb, months_kb, days_kb
from loader import bot, dp, db, scheduler, tz
from my_logger import logger
from zoom import create_meeting, update_meeting_date


@dp.callback_query_handler(text='expert_menu')
async def expert_menu(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "главного меню")

    await call.message.edit_reply_markup()
    await call.message.answer(text="Вы в главном меню. Если захотите сюда вернуться, используйте команду /menu",
                              reply_markup=expert_menu_kb,
                              disable_notification=True)
    logger.debug(f"Expert {user_id} entered expert_menu handler")


def search_applicant(expert_id):
    ed = db.get_expert(expert_id)
    expert_direction = ed[6]

    applicants = db.get_applicants()

    suitable_applicants_same_direction = []
    suitable_applicants_others = []
    for applicant in applicants:
        if applicant[13]:
            applicant_direction = applicant[7]
            if expert_direction == applicant_direction:
                suitable_applicants_same_direction.append(
                    {
                        'user_id': applicant[0],
                        'wr_firstname': applicant[5]
                    }
                )
            else:
                suitable_applicants_others.append(
                    {
                        'user_id': applicant[0],
                        'wr_firstname': applicant[5]
                    }
                )

    suitable_applicants = suitable_applicants_same_direction + suitable_applicants_others

    logger.debug(f"Search_applicant function shows that expert {expert_id} have "
                 f"{len(suitable_applicants)} suitable applicants")

    return suitable_applicants


@dp.callback_query_handler(text='search_applicants')
async def search_applicants(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Посмотреть анкеты соискателей")

    logger.debug(f"Expert {user_id} entered search_applicants handler")
    await call.message.edit_reply_markup()
    suitable_applicants = search_applicant(user_id)
    if suitable_applicants:
        applicant_id = suitable_applicants[0].get('user_id')
        ad = db.get_applicant(applicant_id)
        firstname = ad[5]
        lastname = ad[6]
        direction = ad[7]
        profile = ad[8]
        institution = ad[9]
        grad_year = ad[10]
        empl_region = ad[11]
        hobby = ad[12]
        topics_details = ad[14]

        text = f"<b>Имя:</b> {firstname} {lastname}\n" \
               f"<b>Направление:</b> {direction}\n" \
               f"<b>Опыт:</b> {profile}\n" \
               f"<b>Учебное заведение:</b> {institution}\n" \
               f"<b>Год окончания:</b> {grad_year}\n" \
               f"<b>Регион трудоустройства:</b> {empl_region}\n" \
               f"<b>Хобби:</b> {hobby}\n" \
               f"<b>Вопросы ко встрече:</b> {topics_details}"

        if ad[16]:
            if len(text) <= 1024:
                await call.message.answer_photo(ad[16],
                                                caption=text,
                                                reply_markup=suitable_applicants_kb2(suitable_applicants),
                                                disable_notification=True)
            else:
                await call.message.answer_photo(ad[16])
                await call.message.answer(text=text,
                                          reply_markup=suitable_applicants_kb2(suitable_applicants),
                                          disable_notification=True)
        else:
            await call.message.answer(text=text,
                                      reply_markup=suitable_applicants_kb2(suitable_applicants),
                                      disable_notification=True)

    else:
        await call.message.answer(text="К сожалению, сейчас все соискатели заняты. Пожалуйста, попробуйте позднее.",
                                  reply_markup=kb1b('Назад', "expert_menu"),
                                  disable_notification=True)
        logger.debug(f"Expert {user_id} entered search_applicants handler but don't "
                     f"have any suitable applicants")


@dp.callback_query_handler(Regexp(r'^sakbp_'))
async def page_click_expert(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "⏮/⏭ (соискатели)")

    suitable_applicants = search_applicant(user_id)
    page = int(call.data[6:])
    applicant_id = suitable_applicants[page - 1].get("user_id")
    ad = db.get_applicant(applicant_id)
    firstname = ad[5]
    lastname = ad[6]
    direction = ad[7]
    profile = ad[8]
    institution = ad[9]
    grad_year = ad[10]
    empl_region = ad[11]
    hobby = ad[12]
    topics_details = ad[14]

    text = f"<b>Имя:</b> {firstname} {lastname}\n" \
           f"<b>Направление:</b> {direction}\n" \
           f"<b>Опыт:</b> {profile}\n" \
           f"<b>Учебное заведение:</b> {institution}\n" \
           f"<b>Год окончания:</b> {grad_year}\n" \
           f"<b>Регион трудоустройства:</b> {empl_region}\n" \
           f"<b>Хобби:</b> {hobby}\n" \
           f"<b>Вопросы ко встрече:</b> {topics_details}"

    if ad[16]:
        if len(text) <= 1024:
            await call.message.answer_photo(ad[16],
                                            caption=text,
                                            reply_markup=suitable_applicants_kb2(suitable_applicants, page),
                                            disable_notification=True)
        else:
            await call.message.answer_photo(ad[16])
            await call.message.answer(text=text,
                                      reply_markup=suitable_applicants_kb2(suitable_applicants, page),
                                      disable_notification=True)
    else:
        await call.message.answer(text=text,
                                  reply_markup=suitable_applicants_kb2(suitable_applicants, page),
                                  disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Expert {user_id} entered page_click_expert handler with page {page}")


@dp.callback_query_handler(Regexp(r'^forma_'))
async def choosing_applicant(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Назад (к соискателю)")

    applicant_id = int(call.data[6:])
    ad = db.get_applicant(applicant_id)
    firstname = ad[5]
    lastname = ad[6]
    direction = ad[7]
    profile = ad[8]
    institution = ad[9]
    grad_year = ad[10]
    empl_region = ad[11]
    hobby = ad[12]
    topics_details = ad[14]
    await call.message.answer(text=f"<b>Имя:</b> {firstname} {lastname}\n"
                                   f"<b>Направление:</b> {direction}\n"
                                   f"<b>Опыт:</b> {profile}\n"
                                   f"<b>Учебное заведение:</b> {institution}\n"
                                   f"<b>Год окончания:</b> {grad_year}\n"
                                   f"<b>Регион трудоустройства:</b> {empl_region}\n"
                                   f"<b>Хобби:</b> {hobby}\n"
                                   f"<b>Вопросы ко встрече:</b> {topics_details}\n\n",
                              reply_markup=kb2b("Выбрать соискателя", f'choosea_{applicant_id}',
                                                "Назад", f'search_applicants'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Expert {user_id} entered choosing_applicant handler with applicant {applicant_id}")


@dp.callback_query_handler(Regexp(r'^choosea_'))
async def applicant_chosen(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Выбрать соискателя")

    applicant_id = call.data[8:]
    applicant_agree_to_show_contacts = db.get_applicant(applicant_id)[18]
    if applicant_agree_to_show_contacts:
        kb = kb3b("Отправить приглашение соискателю", f"send_free_slots_{applicant_id}_init_by_e_c_",
                  "Показать контакты", f"show_contacts_a_{applicant_id}", "Назад", f"forma_{applicant_id}")
    else:
        kb = kb2b("Отправить приглашение соискателю", f"send_free_slots_{applicant_id}_init_by_e_c_",
                  "Назад", f"forme_{applicant_id}")

    await call.message.edit_reply_markup()
    await call.message.answer(text="Выбери подходящий пункт",
                              reply_markup=kb,
                              disable_notification=True)

    logger.debug(f"Expert {user_id} entered applicant_chosen handler "
                 f"with applicant {applicant_id}")


@dp.callback_query_handler(Regexp('^precancel_meeting_'))
async def precancel_meeting(call: CallbackQuery):
    user_id = call.from_user.id

    action = call.data.split("_")[2]
    button_text = "Отказать в переносе" if action == "r" else "Отказать во встрече"
    track_user_activity(user_id, "experts", button_text)


    applicant_id = int(call.data.split("_")[3])
    action_text = "Перенос встречи был отменен" if action == "r" else "Встреча была отменена"

    await bot.send_message(applicant_id,
                           "К сожалению, эксперт не сможет встретиться. Давай попробуем назначить встречу "
                           "другому эксперту? Чтобы вернуться в меню, нажми /menu")

    await call.message.edit_reply_markup()
    await call.message.answer(action_text, reply_markup=expert_menu_kb)

    logger.debug(f"Expert {user_id} entered precancel_meeting handler")


@dp.callback_query_handler(Regexp(r'^send_free_slots_'))
async def send_free_slots(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Отправить слоты")

    await call.message.edit_reply_markup()

    async with state.proxy() as data:
        call_data_list = call.data.split("_")

        action = call_data_list[7]
        init_by = call_data_list[6]

        try:
            meeting_id = int(call_data_list[8])
        except ValueError:
            pass
        else:
            data["meeting_id"] = meeting_id

            md = db.get_meeting(meeting_id)
            api_id = md[10]
            if not api_id:
                await call.message.answer("К сожалению, эту встречу невозможно перенести...",
                                          reply_markup=kb1b('Вернуться в главное меню', 'expert_menu'),
                                          disable_notification=True)

                await state.finish()

                return

        data["action"] = action
        data["applicant_id"] = int(call_data_list[3])
        data["init_by"] = init_by
        data["slots"] = set()

    if init_by == "e":
        reply_markup = kb2b(
            "Добавить слоты", "add_new_slots",
            "Назад (отменить отправку временных слотов)", "cancel_sending_slots",
        )
    else:
        reply_markup = kb1b("Добавить слоты", "add_new_slots")

    await call.message.answer(
        f"Введите временные слоты, "
        f"{'когда вам удобно провести' if action == 'c' else 'на которые вы хотите перенести'} "
        f"встречу, желательно указать несколько. <b>Указывайте московское время</b>",
        reply_markup=reply_markup,
    )

    logger.debug(f"Expert {user_id} entered send_free_slots handler")


@dp.callback_query_handler(text='add_new_slots')
async def add_new_slots(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Добавить слоты")

    year = datetime.now(tz=pytz.timezone(tz)).year
    next_year = year + 1
    reply_markup = kb2b(
        str(year), f"choose_slot_year_{year}",
        str(next_year), f"choose_slot_year_{next_year}",
    )

    await call.message.edit_reply_markup()
    await call.message.answer(
        "Выберите год",
        reply_markup=reply_markup,
    )

    logger.debug(f"Expert {user_id} entered send_free_slots handler")


@dp.callback_query_handler(Regexp(r'^choose_slot_year_'))
async def choose_slot_year(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()

    user_id = call.from_user.id

    cd = call.data
    slot_year = int(cd.split("_")[-1])

    current_year = datetime.now().astimezone(timezone(tz)).year
    if current_year > slot_year:
        next_year = current_year + 1
        reply_markup = kb2b(
            str(current_year), f"choose_slot_year_{current_year}",
            str(next_year), f"choose_slot_year_{next_year}",
        )
        await call.message.answer(
            "Год, который Вы выбрали, уже прошел. Выберите год еще раз",
            reply_markup=reply_markup,
        )

        return

    async with state.proxy() as data:
        data["year"] = slot_year

    current_month = datetime.now().astimezone(timezone(tz)).month
    await call.message.answer(
        "Выберите месяц",
        reply_markup=months_kb(current_month),
    )

    logger.debug(f"Expert {user_id} entered choose_slot_year handler")


@dp.callback_query_handler(Regexp(r'^choose_slot_month_'))
async def choose_slot_month(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()

    user_id = call.from_user.id

    cd = call.data
    slot_month = int(cd.split("_")[-1])

    current_month = datetime.now().astimezone(timezone(tz)).month
    if current_month > slot_month:
        await call.message.answer(
            "Месяц, который Вы выбрали, уже прошел. Выберите месяц еще раз",
            reply_markup=months_kb(current_month),
        )

        return

    async with state.proxy() as data:
        slot_year = data["year"]
        data["month"] = slot_month

    current_day = datetime.now().astimezone(timezone(tz)).day
    await call.message.answer(
        "Выберите день",
        reply_markup=days_kb(slot_year, slot_month, current_day),
    )

    logger.debug(f"Expert {user_id} entered choose_slot_month handler")


@dp.callback_query_handler(Regexp(r'^choose_slot_day_'))
async def choose_slot_day(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()

    user_id = call.from_user.id

    cd = call.data
    slot_day = int(cd.split("_")[-1])

    async with state.proxy() as data:
        slot_year = data["year"]
        slot_month = data["month"]

    current_day = datetime.now().astimezone(timezone(tz)).day
    if current_day > slot_day:
        await call.message.answer(
            "День, который Вы выбрали, уже прошел. Выберите день еще раз",
            reply_markup=days_kb(slot_year, slot_month, current_day),
        )

        return

    async with state.proxy() as data:
        data["day"] = slot_day

    await call.message.answer(
        f"Введите через пробел время для выбранной Вами даты - {slot_month:02d}.{slot_year}\n\n"
        "<i>Например, 12:00 14:35</i>",
    )
    await state.set_state("input_time")

    logger.debug(f"Expert {user_id} entered choose_slot_day handler")


@dp.message_handler(state="input_time")
async def choose_slot_time(message: Message, state: FSMContext):
    user_id = message.from_user.id

    await state.reset_state(with_data=False)
    async with state.proxy() as data:
        init_by = data["init_by"]
        slot_year = data["year"]
        slot_month = data["month"]
        slot_day = data["day"]

    slots = set()
    slot_times = message.text.split()
    for time in slot_times:
        try:
            slot_hour, slot_minute = [int(t) for t in time.split(":")]
            slot = datetime(slot_year, slot_month, slot_day, slot_hour, slot_minute).timestamp()
        except ValueError:
            await message.answer(f"Вы допустили ошибку во времени <i>{time}</i>. Пожалуйста, повторите попытку еще раз")
            await state.set_state("input_time")

            return

        if slot < datetime.now().timestamp():
            continue

        slots.add(slot)

    async with state.proxy() as data:
        for s in slots:
            data["slots"].add(s)

        slots_dts = [datetime.fromtimestamp(t) for t in data["slots"]]
        formatted_slots = [f"{dt.day:02d}.{dt.month:02d}.{dt.year} {dt.hour}:{dt.minute:02d}" for dt in slots_dts]

    if formatted_slots:
        text = "Текущие слоты:\n\n" + '\n'.join(formatted_slots)
        if init_by == "e":
            reply_markup = kb3b(
                "Добавить слоты", "add_new_slots",
                "Отправить слоты", "send_slots",
                "Назад (отменить отправку временных слотов)", "cancel_sending_slots",
            )
        else:
            reply_markup = kb2b(
                "Добавить слоты", "add_new_slots",
                "Отправить слоты", "send_slots",
            )
    else:
        text = "Действующие слоты отсутствуют"
        if init_by == "e":
            reply_markup = kb2b(
                "Добавить слоты", "add_new_slots",
                "Назад (отменить отправку временных слотов)", "cancel_sending_slots",
            )
        else:
            reply_markup = kb1b("Добавить слоты", "add_new_slots")

    await message.answer(text, reply_markup=reply_markup)

    logger.debug(f"Expert {user_id} entered choose_slot_time handler")


@dp.callback_query_handler(text='cancel_sending_slots')
async def cancel_sending_slots(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Назад (отменить отправку временных слотов)")

    await state.finish()

    await call.message.edit_reply_markup()
    await call.message.answer(text="Вы в главном меню. Если захотите сюда вернуться, используйте команду /menu",
                              reply_markup=expert_menu_kb,
                              disable_notification=True)


@dp.callback_query_handler(text='cancel_sending_slots')
async def failed_cancel_sending_slots(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Назад (отменить отправку временных слотов)")

    await call.message.edit_reply_markup()
    await call.message.answer(text="Вы уже отправили слоты соискателю и не можете отменить отправку")


@dp.callback_query_handler(text='send_slots')
async def notify_applicant_about_slots(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    async with state.proxy() as data:
        meeting_id = data.get("meeting_id")
        if not meeting_id:
            meeting_id = -1

        action = data["action"]
        applicant_id = data["applicant_id"]
        init_by = data["init_by"]
        slots = data["slots"]

    esl = [datetime.strftime(datetime.fromtimestamp(s).astimezone(timezone(tz)), "%d.%m.%Y %H:%M") for s in slots]
    if not esl:
        return

    ed = db.get_expert(user_id)
    if ed[7]:
        division = ed[7]
    else:
        division = ed[8]

    text = f"Эксперт {ed[5]} отправил тебе временные слоты, " \
           f"{'когда он может провести' if action == 'c' else 'на которые он может перенести'} " \
           "конференцию. Выбери один из них\n\n" \
           "Профиль эксперта:\n\n" \
           f"<b>Имя:</b> {ed[5]}\n" \
           f"<b>Направление:</b> {ed[6]}\n" \
           f"<b>Дивизион:</b> {division}\n" \
           f"<b>Экспертный профиль:</b> {ed[10]}\n"

    if ed[15]:
        if len(text) <= 1024:
            await bot.send_photo(
                applicant_id,
                photo=ed[15],
                caption=text,
                reply_markup=slots_kb(user_id, init_by, esl, action, meeting_id),
            )
        else:
            await bot.send_photo(applicant_id, photo=ed[15])
            await bot.send_message(
                applicant_id,
                text=text,
                reply_markup=slots_kb(user_id, init_by, esl, action, meeting_id),
                disable_notification=True,
            )
    else:
        await bot.send_message(
            applicant_id,
            text=text,
            reply_markup=slots_kb(user_id, init_by, esl, action, meeting_id),
            disable_notification=True,
        )

    db.update_user("experts", "slots", user_id, ",".join(esl))

    await call.message.edit_reply_markup()
    await call.message.answer(
        text="Слоты были отправлены выбранному соискателю. "
             "Оставайтесь на связи, мы сообщим вам о выборе соискателя и дальнейшую "
             "информацию о встрече, если она будет подтверждена",
        reply_markup=kb1b('Вернуться в главное меню', 'expert_menu'),
        disable_notification=True,
    )
    await state.finish()

    logger.debug(
        f"Expert {user_id} entered notify_applicant_about_slots handler and sent slots to applicant {applicant_id}",
    )


@dp.callback_query_handler(text='expert_meetings')
async def expert_meetings(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "отображения действующих встреч")

    await call.message.edit_reply_markup()
    em = db.get_expert_meetings(user_id)
    if em:
        await call.message.answer(text="Ваш список встреч (время по МСК)",
                                  reply_markup=meetings_e_kb(em),
                                  disable_notification=True)
        logger.debug(f"Expert {user_id} entered exert_meetings handler and got {len(em)} his meetings")
    else:
        await call.message.answer(text="У вас пока нет запланированных встреч",
                                  reply_markup=kb1b("Назад", "expert_menu"),
                                  disable_notification=True)
        logger.debug(f"Expert {user_id} entered exert_meetings handler but he doesn't have meetings yet")


@dp.callback_query_handler(Regexp(r'^show_contacts_a_'))
async def show_contacts_a(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Показать контакты")

    db.update_stat("experts")

    applicant_id = int(call.data[16:])
    ad = db.get_applicant(applicant_id)

    await call.answer()
    await call.message.answer(
        f"Если по каким-то причинам Вы хотите связаться с соискателем лично, вот его контакты - @{ad[2]}. "
        "Обратите внимание, если Вы видите @None вместо контакта, значит, с этим пользователем "
        "можно связаться только в запланированной встрече")

    scheduler.add_job(
        notif_after_show_contacts, "date",
        run_date=datetime.now(tz=timezone(tz)) + timedelta(hours=3),
        args=(user_id, applicant_id,),
    )

    logger.debug(f"Expert {user_id} entered show_contacts handler")


@dp.callback_query_handler(Regexp(r'^mkbp_e_'))
async def expert_chosen(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "⏮/⏭ (встречи)")

    page = int(call.data[7:])
    em = db.get_expert_meetings(user_id)
    await call.message.edit_reply_markup(meetings_e_kb(em, page))
    logger.debug(f"Expert {user_id} entered expert_chosen handler with page {page}")


@dp.callback_query_handler(Regexp(r'^meeting_e_'))
async def check_meeting(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "выбора встречи")

    meeting_id = int(call.data[10:])
    md = db.get_meeting(meeting_id)  # meeting's data
    ad = db.get_applicant(md[3])  # applicant's data
    await call.message.answer(text="Информация о встрече\n\n"
                                   f"<b>Дата и время по МСК:</b> {md[4]}\n"
                                   f"<b>Ссылка:</b> {md[6] if md[6] else 'информация отсутствует'}\n\n"
                                   "Соискатель\n\n"
                                   f"<b>Имя:</b> {ad[5]} {ad[6]}\n"
                                   f"<b>Направление:</b> {ad[7]}\n"
                                   f"<b>Опыт:</b> {ad[8]}\n"
                                   f"<b>Учебное заведение:</b> {ad[9]}\n"
                                   f"<b>Год окончания:</b> {ad[10]}\n"
                                   f"<b>Регион трудоустройства:</b> {ad[11]}\n"
                                   f"<b>Хобби:</b> {ad[12]}\n"
                                   f"<b>Вопросы ко встрече:</b> {ad[14]}\n\n",
                              reply_markup=kb3b("Отменить встречу", f'cancel_meeting_e_{md[0]}',
                                                "Перенести встречу", f'send_free_slots_{ad[0]}_init_by_e_r_{meeting_id}',
                                                "Назад", f'expert_meetings'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Expert {user_id} entered check_meeting handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^cancel_meeting_e_'))
async def meeting_cancelation(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Отменить встречу")

    await call.message.edit_reply_markup()
    meeting_id = int(call.data[17:])
    md = db.get_meeting(meeting_id)
    applicant_id = md[3]
    meeting_date = md[4]
    expert_name = db.get_expert(user_id)[5]
    await call.message.answer(text="Встреча отменена.",
                              reply_markup=kb1b("Назад", "expert_menu"))
    db.update_meeting('status', meeting_id, 'Отменена экспертом')
    if md[9] is not None:
        mjl = md[9].split(', ')  # meeting jobs list
        for job in mjl:
            try:
                db.remove_job(job)
                logger.debug(f"Job {job} was removed from job storage")
            except Exception as e:
                logger.warning(f"Job {job} from meeting {meeting_id} was not deleted: {e}")
    await notif_cancel_to_applicant(applicant_id, meeting_date, expert_name)
    logger.debug(f"Expert {user_id} entered meeting_cancelation handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^denied_e_c_'))
@dp.callback_query_handler(Regexp(r'^approved_e_c_'))
async def notif_init_applicant_result(call: CallbackQuery):
    user_id = call.from_user.id

    await call.message.edit_reply_markup()

    cd = call.data.split("_")
    meeting_id = int(cd[3])
    md = db.get_meeting(meeting_id)

    if "approved" in cd:
        track_user_activity(user_id, "experts", "Подтверждаю ✅ (создание встречи)")

        db.update_meeting('status', meeting_id, "Подтверждена")
        db.update_user('applicants', 'status', md[3], 'Встреча подтверждена')

        mddtf = datetime.strptime(md[4], '%d.%m.%Y %H:%M')  # meeting date in datetime format

        mdzf = mddtf.strftime('%Y-%m-%dT%H:%M:%S')  # meeting date in zoom format
        link, api_id = create_meeting(mdzf)
        db.update_meeting('api_id', meeting_id, api_id)
        db.update_meeting('link', meeting_id, link)

        await call.message.answer(f"Встреча была успешно подтверждена. Ссылка: {link}")
        await bot.send_message(md[3], f"Хорошей встречи! Мы будем тебя ждать: {link}")

        notif_1day_time = mddtf - timedelta(days=1)
        notif_3hours_time = mddtf - timedelta(hours=3)
        notif_1hour_time = mddtf - timedelta(hours=1)
        notif_5min_time = mddtf - timedelta(minutes=5)
        feedback_notif_time = mddtf + timedelta(hours=1)

        notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3],))
        notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
        notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
        notif5 = scheduler.add_job(meeting_took_place, "date", run_date=mddtf, args=(meeting_id, md[2], md[3]))
        notif6 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(meeting_id,))
        notif7 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(meeting_id,))

        db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}, {notif3.id}, {notif4.id}, {notif5.id}, {notif6.id}, {notif7}')
    if "denied" in cd:
        track_user_activity(user_id, "experts", "Не подтверждаю ❌ (создание встречи)")

        db.update_meeting('status', meeting_id, "Отклонена экспертом")
        await call.message.answer(text="Встреча отменена")
        db.update_user('applicants', 'status', md[3], 'Эксперт отменил последнюю встречу')
        await notif_cancel_to_applicant2(md[3])

    logger.debug(
        f"Expert {user_id} entered notif_init_applicant_result with meeting {meeting_id} and cd {cd}")


def meeting_took_place(meeting_id, expert_id, applicant_id):
    meeting_ids = [meeting[0] for meeting in db.get_expert_meetings(expert_id)]

    if meeting_id in meeting_ids:
        db.update_meeting("status", meeting_id, 'Состоялась')

    db.update_user('applicants', 'status', applicant_id, 'Последняя встреча состоялась')


@dp.callback_query_handler(Regexp(r'^denied_e_r_'))
@dp.callback_query_handler(Regexp(r'^approved_e_r_'))
async def notif_reschedule_applicant_result(call: CallbackQuery):
    user_id = call.from_user.id

    await call.message.edit_reply_markup()

    cd = call.data.split("_")
    meeting_id = int(cd[3])
    md = db.get_meeting(meeting_id)

    if "approved" in cd:
        track_user_activity(user_id, "experts", "Подтверждаю ✅ (перенос встречи)")

        new_start_timestamp = float(cd[4])
        new_start_dt = datetime.fromtimestamp(new_start_timestamp).astimezone(timezone(tz))
        mddbf = new_start_dt.strftime('%d.%m.%Y %H:%M')
        mdzf = new_start_dt.strftime('%Y-%m-%dT%H:%M:%S')

        api_id = md[10]

        update_meeting_date(api_id, mdzf)

        db.update_meeting('status', meeting_id, "Перенесена")
        db.update_meeting('meeting_date', meeting_id, mddbf)

        db.update_user('applicants', 'status', md[3], 'Встреча перенесена')

        if md[9] is not None:
            mjl = md[9].split(', ')  # meeting jobs list
            for job in mjl:
                try:
                    db.remove_job(job)
                    logger.debug(f"Job {job} was removed from job storage")
                except Exception as e:
                    logger.warning(f"Job {job} from meeting {meeting_id} was not deleted: {e}")

        await call.message.answer("Встреча была успешно перенесена")
        await bot.send_message(md[3], "Твоя встреча была успешно перенесена! Информацию о перенесенной встрече можно "
                                      "посмотреть в разделе 'Мои встречи'")

        notif_1day_time = new_start_dt - timedelta(days=1)
        notif_3hours_time = new_start_dt - timedelta(hours=3)
        notif_1hour_time = new_start_dt - timedelta(hours=1)
        notif_5min_time = new_start_dt - timedelta(minutes=5)
        feedback_notif_time = new_start_dt + timedelta(hours=1)

        notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], meeting_id))
        notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
        notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
        notif5 = scheduler.add_job(meeting_took_place, "date", run_date=new_start_dt, args=(meeting_id, md[2], md[3]))
        notif6 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(meeting_id,))
        notif7 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(meeting_id,))

        db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}, {notif3.id}, {notif4.id}, {notif5.id}, {notif6.id}, {notif7.id}')
    if "denied" in cd:
        track_user_activity(user_id, "experts", "Не подтверждаю ❌ (перенос встречи)")

        db.update_meeting('status', meeting_id, "Отклонена экспертом (перенос)")
        await call.message.answer(text="Перенос встречи отменен")
        db.update_user('applicants', 'status', md[3], 'Эксперт отменил перенос последней встречи')
        await notif_cancel_to_applicant3(md[3])

    logger.debug(
        f"Expert {user_id} entered notif_reschedule_applicant_result with meeting {meeting_id} and cd {cd}")


@dp.callback_query_handler(Regexp(r'^expert_fb_agree_'))
async def expert_fb_agree(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Оставить отзыв")

    cd = call.data
    meeting_id = cd[16:]
    db.update_meeting('expert_fb', meeting_id, 'Ожидает отзыва')
    await call.message.answer("Напишите ваш отзыв в ответом письме:")
    await state.set_state(f"expert_writing_feedback")
    async with state.proxy() as data:
        data["fb_meeting_id"] = meeting_id

    await call.message.edit_reply_markup()
    logger.debug(f"Expert {user_id} entered expert_fb_agree with meeting {meeting_id}")


@dp.message_handler(state="expert_writing_feedback")
async def expert_writing_feedback(message: Message, state: FSMContext):
    fb = message.text

    data = await state.get_data()
    meeting_id = data["fb_meeting_id"]

    await message.answer("Спасибо за ваш отзыв! Вы делаете работу сервиса лучше.",
                         reply_markup=expert_menu_kb)
    db.update_meeting("expert_fb", meeting_id, fb)
    await state.finish()
    logger.debug(f"Expert {message.from_user.id} entered expert_writing_feedback with meeting {meeting_id}")


@dp.callback_query_handler(text='add_photo_e')
async def add_photo(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Добавить фото к анкете")

    logger.debug(f"Expert {user_id} entered add_photo handler")
    await call.message.edit_reply_markup()
    ed = db.get_expert(user_id)
    photo = ed[15]
    if photo:
        await call.message.answer_photo(photo, "Ваша текущая фотография. Желаете изменить?",
                                        reply_markup=kb2b("Изменить", "update_photo_e", "Назад", "expert_menu"),
                                        disable_notification=True)
    else:
        await call.message.answer("У вас пока нет фотографии. Желаете добавить?",
                                  reply_markup=kb2b("Добавить фото", "update_photo_e", "Назад", "expert_menu"),
                                  disable_notification=True)


@dp.callback_query_handler(text='update_photo_e')
async def update_photo(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    track_user_activity(user_id, "experts", "Добавить фото")

    logger.debug(f"Expert {user_id} entered update_photo handler")
    await call.message.edit_reply_markup()
    await call.message.answer("Пожалуйста, пришлите фотографию в чат (не файлом)",
                              disable_notification=True)
    await state.set_state('uploading_photo_e')


@dp.message_handler(state='uploading_photo_e', content_types=['photo'])
async def uploading_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id

    logger.debug(f"Expert {user_id} entered uploading_photo handler")
    photo_id = message.photo[-1].file_id
    db.update_user('experts', 'photo', user_id, photo_id)
    await message.answer('Ваша фотография успешно обновлена', reply_markup=expert_menu_kb, disable_notification=True)
    await state.finish()


@dp.message_handler(state='uploading_photo_e')
async def uploading_photo_msg(message: Message, state: FSMContext):
    logger.debug(f"Expert {message.from_user.id} entered uploading_photo_msg handler")
    await message.answer("Бот вас не понял. Пожалуйста, пришлите фото в этот чат (не ссылкой и не файлом). "
                         "Попробуйте снова или вернитесь в главное меню.",
                         disable_notification=True,
                         reply_markup=kb2b("Добавить фото", "update_photo_e", "Назад", "expert_menu"))
    await state.finish()


@dp.callback_query_handler(text='change_agreement_to_show_contacts_e')
async def change_agreement_to_show_contacts(call: CallbackQuery):
    expert_id = call.from_user.id
    expert_agree_to_show_contacts = db.get_expert(expert_id)[18]
    if expert_agree_to_show_contacts:
        text = f"Нажмите \"Нет\", если вы не хотите, чтобы вам писали соискатели в телеграм (@{call.from_user.username})"
        kb = kb2b("Нет", "change_agreement_e", "Назад", "expert_menu")
    else:
        text = "Нажмите \"Да\", чтобы мы могли показывать ваши контактные данные в телеграм " \
               f"(@{call.from_user.username}) соискателям. Так они смогут связаться с вами, если " \
               "проблема с конференцией"
        kb = kb2b("Да", "change_agreement_e", "Назад", "expert_menu")

    await call.message.edit_reply_markup()
    await call.message.answer(text, reply_markup=kb)

    logger.debug(f"Expert {expert_id} entered change_agreement_to_show_contacts")


@dp.callback_query_handler(text='change_agreement_e')
async def proceed_changing_agreement_to_show_contacts(call: CallbackQuery):
    expert_id = call.from_user.id
    expert_agree_to_show_contacts = db.get_expert(expert_id)[18]
    if expert_agree_to_show_contacts:
        new_agreement_status = False
    else:
        new_agreement_status = True

    db.update_user('experts', 'agree_to_show_contacts', expert_id, new_agreement_status)

    await call.message.edit_reply_markup()
    await call.message.answer("Статус согласия был успешно изменен", reply_markup=expert_menu_kb)

    logger.debug(f"Expert {expert_id} entered proceed_changing_agreement_to_show_contacts")
