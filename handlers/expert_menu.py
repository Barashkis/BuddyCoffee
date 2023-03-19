import re
from datetime import datetime, timedelta

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import Message, CallbackQuery

from handlers.notifications import notif_cancel_to_applicant, notif_1day, \
    notif_3hours, notif_cancel_to_applicant2, notif_after_show_contacts, notif_1hour, notif_5min, \
    feedback_notif_applicant, feedback_notif_expert, notif_cancel_to_applicant3
from handlers.utils import track_user_activity
from keyboards import expert_menu_kb, kb1b, kb3b, suitable_applicants_kb2, kb2b, meetings_e_kb, \
    slots_kb
from loader import bot, dp, db, scheduler
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

    await call.message.edit_reply_markup()
    await call.message.answer(text="Выбери подходящий пункт",
                              reply_markup=kb3b("Отправить приглашение соискателю",
                                                f"send_free_slots_{applicant_id}_init_by_e_c_",
                                                "Показать контакты", f"show_contacts_a_{applicant_id}",
                                                "Назад", f"forma_{applicant_id}"),
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

    await state.set_state('input_slots')
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

    kwargs = {}
    if init_by == "e":
        kwargs["reply_markup"] = kb1b("Назад (отменить отправку временных слотов)", "cancel_sending_slots")

    await call.message.answer(f"Введите временные слоты, "
                              f"{'когда вам удобно провести' if action == 'c' else 'на которые вы хотите перенести'}"
                              f"встречу, желательно указать несколько. <b>Укажите московское время</b>\n\n"
                              "<i>Формат:\n"
                              "25.01.2022 17:00, 27.01.2022 12:30, "
                              "28.01.2022 10:00, 31.01.2022 10:45, 02.02.2022 16:15</i>",
                              **kwargs)

    logger.debug(f"Expert {user_id} entered send_free_slots handler")


@dp.callback_query_handler(text='cancel_sending_slots', state='input_slots')
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


@dp.message_handler(state='input_slots')
async def notify_applicant_about_slots(message: Message, state: FSMContext):
    user_id = message.from_user.id

    async with state.proxy() as data:
        meeting_id = data.get("meeting_id")
        if not meeting_id:
            meeting_id = -1

        action = data["action"]
        applicant_id = data["applicant_id"]
        init_by = data["init_by"]

    message_text = message.text
    try:
        slots_list = message_text.split(',')
        slots_list = [slot.lstrip().rstrip() for slot in slots_list]
        esl = []
        for slot in slots_list:
            if not re.match("^\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}$", slot):
                await message.answer(text=f'Бот не смог распознать следующий слот: <i>{slot}</i>\n\n'
                                          'Пожалуйста, придерживайтесь формата. Отправьте временные слоты еще раз',
                                     disable_notification=True)
                await state.set_state('input_slots')
                logger.debug(
                    f"Expert {user_id} entered notify_applicant_about_slots handler but write incorrect slot: {slot}")

                return

            if datetime.strptime(slot, '%d.%m.%Y %H:%M') > datetime.today().astimezone(pytz.timezone('Europe/Moscow')).replace(tzinfo=None):
                esl.append(slot)

        if esl:
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
                    await bot.send_photo(applicant_id,
                                         photo=ed[15],
                                         caption=text,
                                         reply_markup=slots_kb(user_id, init_by, esl, action, meeting_id))
                else:
                    await bot.send_photo(applicant_id, photo=ed[15])
                    await bot.send_message(applicant_id,
                                           text=text,
                                           reply_markup=slots_kb(user_id, init_by, esl, action, meeting_id),
                                           disable_notification=True)
            else:
                await bot.send_message(applicant_id,
                                       text=text,
                                       reply_markup=slots_kb(user_id, init_by, esl, action, meeting_id),
                                       disable_notification=True)

            db.update_user("experts", "slots", user_id, message_text)

            await message.answer(text="Слоты были отправлены выбранному соискателю. "
                                      "Оставайтесь на связи, мы сообщим вам о выборе соискателя и дальнейшую "
                                      "информацию о встрече, если она будет подтверждена",
                                 reply_markup=kb1b('Вернуться в главное меню', 'expert_menu'),
                                 disable_notification=True)
            await state.finish()

            logger.debug(
                f"Expert {user_id} entered notify_applicant_about_slots handler and sent slots to applicant {applicant_id}")
        else:
            logger.warning(
                f"Expert {user_id} entered notify_applicant_about_slots handler but slots is overdue")
            await message.answer(text='Ни один из введенных Вами слотов не является действующим. '
                                      'Отправьте временные слоты еще раз',
                                 disable_notification=True)
            await state.set_state('input_slots')

    except Exception as e:
        logger.warning(
            f"Expert {user_id} entered notify_applicant_about_slots handler but got an error: {e}")
        await message.answer(text=f'Бот не смог распознать ваш ответ\n\n'
                                  f'Пожалуйста, придерживайтесь формата. Отправьте временные слоты еще раз',
                             disable_notification=True)
        await state.set_state('input_slots')


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

    local_now = datetime.now()
    now = local_now.astimezone(pytz.timezone('Europe/Moscow')).replace(tzinfo=None)

    notif_date = now + timedelta(hours=3)
    scheduler.add_job(notif_after_show_contacts, "date", run_date=notif_date, args=(user_id, applicant_id,))

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
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], md[0]))
        notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
        notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
        notif5 = scheduler.add_job(meeting_took_place, "date", run_date=mddtf, args=(meeting_id, md[2], md[3]))
        notif6 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(md[0],))
        notif7 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(md[0],))

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

        new_start_time = cd[4].replace("%", ":")
        mdzf = datetime.strptime(new_start_time, '%d.%m.%Y %H:%M').strftime('%Y-%m-%dT%H:%M:%S')

        api_id = md[10]

        update_meeting_date(api_id, mdzf)

        db.update_meeting('status', meeting_id, "Перенесена")
        db.update_meeting('meeting_date', meeting_id, new_start_time)

        db.update_user('applicants', 'status', md[3], 'Встреча перенесена')

        if md[9] is not None:
            mjl = md[9].split(', ')  # meeting jobs list
            for job in mjl:
                try:
                    db.remove_job(job)
                    logger.debug(f"Job {job} was removed from job storage")
                except Exception as e:
                    logger.warning(f"Job {job} from meeting {meeting_id} was not deleted: {e}")

        mddtf = datetime.strptime(new_start_time, '%d.%m.%Y %H:%M')  # meeting date in datetime format

        await call.message.answer("Встреча была успешно перенесена")
        await bot.send_message(md[3], "Твоя встреча была успешно перенесена! Информацию о перенесенной встрече можно "
                                      "посмотреть в разделе 'Мои встречи'")

        notif_1day_time = mddtf - timedelta(days=1)
        notif_3hours_time = mddtf - timedelta(hours=3)
        notif_1hour_time = mddtf - timedelta(hours=1)
        notif_5min_time = mddtf - timedelta(minutes=5)
        feedback_notif_time = mddtf + timedelta(hours=1)

        notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], md[0]))
        notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
        notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
        notif5 = scheduler.add_job(meeting_took_place, "date", run_date=mddtf, args=(meeting_id, md[2], md[3]))
        notif6 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(md[0],))
        notif7 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(md[0],))

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
