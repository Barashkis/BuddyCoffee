import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import CallbackQuery, Message
from datetime import datetime, timedelta

from handlers.utils import track_user_activity
from handlers.notifications import notif_init_expert, \
    notif_cancel_to_expert, notif_cancel_to_expert2, notif_3hours, notif_1day, notif_5min, notif_1hour, \
    feedback_notif_applicant, feedback_notif_expert, notif_init_applicant, notif_after_show_contacts, \
    notif_reschedule_applicant, notif_reschedule_expert, notif_cancel_to_expert3
from keyboards import applicant_menu_kb, kb1b, kb2b, kb3b, slots_kb, choosing_time_cd, meetings_a_kb, \
    suitable_experts_kb2
from loader import dp, db, scheduler, bot, tz
import pytz
import re

from my_logger import logger
from zoom import create_meeting, update_meeting_date


@dp.callback_query_handler(text='applicant_menu')
async def applicant_menu(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "главного меню")

    await call.message.edit_reply_markup()
    await call.message.answer(text="Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu",
                              reply_markup=applicant_menu_kb,
                              disable_notification=True)
    logger.debug(f"Applicant {user_id} entered applicant_menu handler")


def search_expert(applicant_id):
    ad = db.get_applicant(applicant_id)
    applicant_direction = ad[7]

    experts = db.get_experts()

    suitable_experts_same_direction = []
    suitable_experts_others = []
    for expert in experts:
        if expert[14] not in ["На модерации", "Заполняет анкету"] and expert[12] is not None:
            expert_direction = expert[6]
            if applicant_direction == expert_direction:
                suitable_experts_same_direction.append(
                    {
                        'user_id': expert[0],
                        'fullname': expert[5]
                    }
                )
            else:
                suitable_experts_others.append(
                    {
                        'user_id': expert[0],
                        'fullname': expert[5]
                    }
                )

    suitable_experts = suitable_experts_same_direction + suitable_experts_others

    logger.debug(f"Search_expert function shows that expert {applicant_id} have "
                 f"{len(suitable_experts)} suitable experts")

    return suitable_experts


@dp.callback_query_handler(text='search_experts')
async def search_experts(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Начать поиск специалистов")

    logger.debug(f"Applicant {user_id} entered search_experts handler")
    suitable_experts = search_expert(user_id)
    if suitable_experts:
        expert_id = suitable_experts[0].get("user_id")
        ed = db.get_expert(expert_id)
        if ed[7]:
            division = ed[7]
        else:
            division = ed[8]

        text = f"<b>Имя:</b> {ed[5]}\n" \
               f"<b>Направление:</b> {ed[6]}\n" \
               f"<b>Дивизион:</b> {division}\n" \
               f"<b>Экспертный профиль:</b> {ed[10]}\n"

        if ed[15]:
            if len(text) <= 1024:
                await call.message.answer_photo(ed[15],
                                                caption=text,
                                                reply_markup=suitable_experts_kb2(suitable_experts),
                                                disable_notification=True)
            else:
                await call.message.answer_photo(ed[15])
                await call.message.answer(text=text,
                                          reply_markup=suitable_experts_kb2(suitable_experts),
                                          disable_notification=True)
        else:
            await call.message.answer(text=text,
                                      reply_markup=suitable_experts_kb2(suitable_experts),
                                      disable_notification=True)
        await call.message.edit_reply_markup()
    else:
        await call.message.answer(text="К сожалению, все эксперты по выбранному направлению заняты. Пожалуйста, "
                                       "попробуй записаться позднее или выбрать другое направление. Следи за "
                                       "уведомлениями — мы регулярно проводим мастер-классы и увеличиваем "
                                       "количество специалистов для проведения консультации",
                                  reply_markup=kb1b('Назад', "applicant_menu"),
                                  disable_notification=True)
        logger.debug(f"Applicant {user_id} entered search_experts handler but don't "
                     f"have any suitable experts")
        await call.message.edit_reply_markup()


@dp.callback_query_handler(Regexp(r'^sekbp_'))
async def page_click_applicant(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "⏮/⏭ (эксперты)")

    suitable_experts = search_expert(user_id)
    page = int(call.data[6:])
    expert_id = suitable_experts[page - 1].get("user_id")
    ed = db.get_expert(expert_id)
    if ed[7]:
        division = ed[7]
    else:
        division = ed[8]

    text = f"<b>Имя:</b> {ed[5]}\n" \
           f"<b>Направление:</b> {ed[6]}\n" \
           f"<b>Дивизион:</b> {division}\n" \
           f"<b>Экспертный профиль:</b> {ed[10]}\n"

    if ed[15]:
        if len(text) <= 1024:
            await call.message.answer_photo(ed[15],
                                            caption=text,
                                            reply_markup=suitable_experts_kb2(suitable_experts, page),
                                            disable_notification=True)
        else:
            await call.message.answer_photo(ed[15])
            await call.message.answer(text=text,
                                      reply_markup=suitable_experts_kb2(suitable_experts, page),
                                      disable_notification=True)
    else:
        await call.message.answer(text=text,
                                  reply_markup=suitable_experts_kb2(suitable_experts, page),
                                  disable_notification=True)

    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {user_id} entered page_click_applicant handler with page {page}")


@dp.callback_query_handler(Regexp(r'^forme_'))
async def choosing_expert(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Назад (к эксперту)")

    expert_id = int(call.data[6:])
    ed = db.get_expert(expert_id)
    if ed[7]:
        division = ed[7]
    else:
        division = ed[8]
    await call.message.answer(text=f"<b>Имя:</b> {ed[5]}\n"
                                   f"<b>Направление:</b> {ed[6]}\n"
                                   f"<b>Дивизион:</b> {division}\n"
                                   f"<b>Экспертный профиль:</b> {ed[10]}\n",
                              reply_markup=kb2b("Выбрать специалиста", f'choosee_{expert_id}',
                                                "Назад", f'search_experts'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {user_id} entered choosing_expert handler with expert {expert_id}")


@dp.callback_query_handler(Regexp(r'^choosee_'))
async def expert_chosen(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Выбрать")

    cd = call.data
    expert_id = int(cd[8:])
    expert_agree_to_show_contacts = db.get_expert(expert_id)[18]
    if expert_agree_to_show_contacts:
        kb = kb3b("Отправить приглашение эксперту", f"send_invitation_{expert_id}_c",
                  "Показать контакты", f"show_contacts_e_{expert_id}", "Назад", f"forme_{expert_id}")
    else:
        kb = kb2b("Отправить приглашение эксперту", f"send_invitation_{expert_id}_c",
                  "Назад", f"forme_{expert_id}")

    await call.message.edit_reply_markup()
    await call.message.answer(text="Выбери подходящий пункт",
                              reply_markup=kb,
                              disable_notification=True)
    logger.debug(f"Applicant {user_id} entered expert_chosen handler "
                 f"with expert {expert_id}")


@dp.callback_query_handler(Regexp(r'^send_invitation_'))
async def sending_invitation(call: CallbackQuery):
    await call.message.edit_reply_markup()

    applicant_id = call.from_user.id
    track_user_activity(applicant_id, "applicants", "Отправить приглашение эксперту")

    call_data_list = call.data.split("_")

    expert_id = int(call_data_list[2])
    action = call_data_list[3]
    precancel_button_text = "Отказать в переносе" if action == "r" else "Отказать во встрече"

    try:
        meeting_id = int(call_data_list[4])
    except IndexError:
        meeting_id = ""
    else:
        md = db.get_meeting(meeting_id)
        api_id = md[10]
        if not api_id:
            await call.message.answer("К сожалению, эту встречу невозможно перенести...",
                                      reply_markup=kb1b('Вернуться в главное меню', 'applicant_menu'),
                                      disable_notification=True)

            return

    applicant_name = db.get_applicant(applicant_id)[5]

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

    text = f"Соискатель {applicant_name} хочет {'с вами встретиться' if action == 'c' else 'перенести встречу с вами'}\n\n" \
           "Профиль соискателя:\n\n" \
           f"<b>Имя:</b> {firstname} {lastname}\n" \
           f"<b>Направление:</b> {direction}\n" \
           f"<b>Опыт:</b> {profile}\n" \
           f"<b>Учебное заведение:</b> {institution}\n" \
           f"<b>Год окончания:</b> {grad_year}\n" \
           f"<b>Регион трудоустройства:</b> {empl_region}\n" \
           f"<b>Хобби:</b> {hobby}\n" \
           f"<b>Вопросы ко встрече:</b> {topics_details}\n\n"

    if ad[16]:
        if len(text) <= 1024:
            await bot.send_photo(expert_id,
                                 photo=ad[16],
                                 caption=text,
                                 reply_markup=kb2b("Отправить слоты", f"send_free_slots_{applicant_id}_init_by_a_{action}_{meeting_id}", precancel_button_text, f"precancel_meeting_{action}_{applicant_id}"))
        else:
            await bot.send_photo(expert_id, photo=ad[16])
            await bot.send_message(expert_id,
                                   text=text,
                                   reply_markup=kb2b("Отправить слоты", f"send_free_slots_{applicant_id}_init_by_a_{action}_{meeting_id}", precancel_button_text, f"precancel_meeting_{action}_{applicant_id}"),
                                   disable_notification=True)
    else:
        await bot.send_message(expert_id,
                               text=text,
                               reply_markup=kb2b("Отправить слоты", f"send_free_slots_{applicant_id}_init_by_a_{action}_{meeting_id}", precancel_button_text, f"precancel_meeting_{action}_{applicant_id}"),
                               disable_notification=True)

    await call.message.answer(f"{'Приглашение провести' if action == 'c' else 'Предложение перенести'} "
                              f"конференцию было отправлено выбранному эксперту. "
                              f"Вскоре он предложит возможные даты {' ее проведения' if action == 'c' else ''}. "
                              f"Мы оповестим тебя, когда придет время выбора времени!",
                              reply_markup=kb1b('Вернуться в главное меню', 'applicant_menu'),
                              disable_notification=True)

    logger.debug(f"Applicant {applicant_id} entered send_invitation handler to hire with expert {expert_id}")


@dp.callback_query_handler(Regexp(r'^skbp_'))
async def expert_chosen(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "⏮/⏭ (слоты)")

    expert_id = int(re.split('_', call.data)[1])
    init_by = re.split('_', call.data)[5]
    slots = db.get_expert(expert_id)[11].split(', ')
    page = int(re.split('_', call.data)[2])
    action = re.split('_', call.data)[6]
    meeting_id = int(re.split('_', call.data)[7])
    await call.message.edit_reply_markup(slots_kb(expert_id, init_by, slots, action, meeting_id, page))
    logger.debug(f"Applicant {user_id} entered expert_chosen handler with page {page}")


@dp.callback_query_handler(choosing_time_cd.filter())
async def choosing_time(call: CallbackQuery, callback_data: dict):
    await call.message.edit_reply_markup()

    applicant_id = call.from_user.id
    track_user_activity(applicant_id, "applicants", "выбора слота")

    init_by = callback_data.get('init_by')
    expert_id = callback_data.get('expert_id')
    slot = callback_data.get('slot').replace("%", ":")
    td = datetime.now(tz=pytz.timezone(tz)).strftime('%d.%m.%Y')
    action = callback_data.get('action')

    expert_fullname = db.get_expert(expert_id)[5]
    applicant_name = db.get_applicant(applicant_id)[5]

    if action == "c":
        meeting_status = 'Инициирована экспертом' if init_by == "expert" else 'Инициирована соискателем'

        db.add_meeting(td, expert_id, applicant_id, slot, meeting_status)
        meeting_id = db.get_last_insert_meeting_id(expert_id, applicant_id)[0]

        if init_by == "e":
            await notif_init_applicant(applicant_id, slot, expert_fullname, meeting_id)
        else:
            db.update_user('applicants', 'status', applicant_id, 'Инициировал встречу')

            await notif_init_expert(expert_id, slot, applicant_name, meeting_id)
    else:
        meeting_id = int(callback_data.get('meeting_id'))
        meeting_status = 'Инициирована экспертом (перенос)' if init_by == "expert" else 'Инициирована соискателем (перенос)'

        db.update_meeting('status', meeting_id, meeting_status)

        if init_by == "e":
            await notif_reschedule_applicant(applicant_id, slot, expert_fullname, meeting_id)
        else:
            db.update_user('applicants', 'status', applicant_id, 'Инициировал перенос встречи')

            await notif_reschedule_expert(expert_id, slot, applicant_name, meeting_id)

    await call.message.answer(text="Отличный выбор! Оставайся на связи, мы напомним тебе о встрече! "
                                   "Если хочешь перенести или отменить встречу, выбери пункт в меню 'Мои встречи'",
                              reply_markup=kb1b('Вернуться в главное меню', 'applicant_menu'),
                              disable_notification=True)

    logger.debug(f"Applicant {applicant_id} entered choosing_time handler "
                 f"with expert {expert_id} and {slot} slot")


@dp.callback_query_handler(text='applicant_meetings')
async def applicant_meetings(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "отображения действующих встреч")

    await call.message.edit_reply_markup()
    am = db.get_applicant_meetings(user_id)
    if am:
        await call.message.answer(text="Ваш список встреч. <b>Указано московское время</b>",
                                  reply_markup=meetings_a_kb(am),
                                  disable_notification=True)
        logger.debug(f"Applicant {user_id} entered applicant_meetings handler and got {len(am)} his meetings")
    else:
        await call.message.answer(text="У тебя пока нет запланированных встреч",
                                  reply_markup=kb1b("Назад", "applicant_menu"),
                                  disable_notification=True)
    logger.debug(f"Applicant {user_id} entered applicant_meetings handler but he doesn't have meetings yet")


@dp.callback_query_handler(Regexp(r'^show_contacts_e_'))
async def show_contacts_a(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Показать контакты")

    db.update_stat("applicants")

    expert_id = int(call.data[16:])
    ed = db.get_expert(expert_id)

    await call.answer()
    await call.message.answer(f"Если по каким-то причинам ты хочешь связаться с экспертом лично, вот его контакты - @{ed[2]}. "
                              "Обрати внимание, если ты видишь @None вместо контакта, значит, с этим пользователем "
                              "можно связаться, только запланировав встречу в нашем боте")

    scheduler.add_job(
        notif_after_show_contacts, "date",
        run_date=datetime.now(tz=pytz.timezone(tz)) + timedelta(hours=3),
        args=(user_id, expert_id,),
    )

    logger.debug(f"Applicant {user_id} entered show_contacts handler")


@dp.callback_query_handler(Regexp(r'^mkbp_a_'))
async def expert_chosen(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "⏮/⏭ (встречи)")

    page = int(call.data[7:])
    am = db.get_applicant_meetings(user_id)
    await call.message.edit_reply_markup(meetings_a_kb(am, page))
    logger.debug(f"Applicant {user_id} entered expert_chosen handler with page {page}")


@dp.callback_query_handler(Regexp(r'^meeting_a_'))
async def check_meeting(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "выбора встречи")

    meeting_id = int(call.data[10:])
    md = db.get_meeting(meeting_id)  # meeting's data
    ed = db.get_expert(md[2])  # expert's data
    await call.message.answer(text="Информация о встрече\n\n"
                                   f"<b>Дата и время по МСК:</b> {md[4]}\n"
                                   f"<b>Ссылка:</b> {md[6] if md[6] else 'информация отсутствует'}\n\n"
                                   "Специалист\n\n"
                                   f"<b>Имя:</b> {ed[5]}\n"
                                   f"<b>Направление:</b> {ed[6]}\n"
                                   f"<b>Дивизион:</b> {ed[7] if ed[7] else ed[8]}\n"
                                   f"<b>Экспертный профиль:</b> {ed[10]}",
                              reply_markup=kb3b("Отменить встречу", f'cancel_meeting_a_{md[0]}',
                                                "Перенести встречу", f"send_invitation_{ed[0]}_r_{meeting_id}",
                                                "Назад", f'applicant_meetings'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {user_id} entered check_meeting handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^cancel_meeting_a_'))
async def meeting_cancelation(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Отменить встречу")

    await call.message.edit_reply_markup()
    meeting_id = int(call.data[17:])
    md = db.get_meeting(meeting_id)
    expert_id = md[2]
    meeting_date = md[4]
    applicant_name = db.get_applicant(user_id)[5]
    await call.message.answer(text="Встреча отменена",
                              reply_markup=kb1b("Назад", "applicant_menu"))
    db.update_meeting('status', meeting_id, 'Отменена соискателем')
    db.update_user('applicants', 'status', user_id, 'Отменил последнюю встречу')
    await notif_cancel_to_expert(expert_id, meeting_date, applicant_name)
    if md[9] is not None:
        mjl = md[9].split(', ')  # meeting jobs list
        for job in mjl:
            try:
                db.remove_job(job)
                logger.debug(f"Job {job} was removed from job storage")
            except Exception as e:
                logging.warning(f"Job {job} from meeting {meeting_id} was not deleted: {e}")
    logger.debug(f"Applicant {user_id} entered meeting_cancelation handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^denied_a_c_'))
@dp.callback_query_handler(Regexp(r'^approved_a_c_'))
async def notif_init_expert_result(call: CallbackQuery):
    user_id = call.from_user.id

    await call.message.edit_reply_markup()

    cd = call.data.split("_")
    meeting_id = int(cd[3])
    md = db.get_meeting(meeting_id)

    if "approved" in cd:
        track_user_activity(user_id, "applicants", "Подтверждаю ✅ (создание встречи)")

        db.update_meeting('status', meeting_id, "Подтверждена")
        db.update_user('applicants', 'status', user_id, 'Встреча подтверждена')

        mddtf = datetime.strptime(md[4], '%d.%m.%Y %H:%M')  # meeting date in datetime format

        mdzf = mddtf.strftime('%Y-%m-%dT%H:%M:%S')  # meeting date in zoom format
        link, api_id = create_meeting(mdzf)
        db.update_meeting('api_id', meeting_id, api_id)
        db.update_meeting('link', meeting_id, link)

        await call.message.answer(f"Хорошей встречи! Мы будем тебя ждать: {link}")
        await bot.send_message(md[2], f"Встреча была успешно подтверждена. Ссылка: {link}")

        notif_1day_time = mddtf - timedelta(days=1)
        notif_3hours_time = mddtf - timedelta(hours=3)
        notif_1hour_time = mddtf - timedelta(hours=1)
        notif_5min_time = mddtf - timedelta(minutes=5)
        feedback_notif_time = mddtf + timedelta(hours=1)

        notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], md[0]))
        notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
        notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
        notif5 = scheduler.add_job(meeting_took_place, "date", run_date=mddtf, args=(meeting_id, md[3],))
        notif6 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(md[0],), misfire_grace_time=59)
        notif7 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(md[0],), misfire_grace_time=59)

        db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}, {notif3.id}, {notif4.id}, {notif5.id}, {notif6.id}, {notif7.id}')
    if "denied" in cd:
        track_user_activity(user_id, "applicants", "Не подтверждаю ❌ (создание встречи)")

        db.update_meeting('status', meeting_id, "Отклонена соискателем")
        await call.message.answer(text="Встреча отменена")
        await notif_cancel_to_expert2(md[2])
        db.update_user('applicants', 'status', user_id, 'Отменил последнюю встречу')

    logger.debug(
        f"Applicant {user_id} entered notif_init_expert_result with meeting {meeting_id} and cd {cd}")


def meeting_took_place(meeting_id, applicant_id):
    meeting_ids = [meeting[0] for meeting in db.get_applicant_meetings(applicant_id)]

    if meeting_id in meeting_ids:
        db.update_meeting("status", meeting_id, 'Состоялась')

    db.update_user('applicants', 'status', applicant_id, 'Последняя встреча состоялась')


@dp.callback_query_handler(Regexp(r'^denied_a_r_'))
@dp.callback_query_handler(Regexp(r'^approved_a_r_'))
async def notif_reschedule_expert_result(call: CallbackQuery):
    user_id = call.from_user.id

    await call.message.edit_reply_markup()

    cd = call.data.split("_")
    meeting_id = int(cd[3])
    md = db.get_meeting(meeting_id)

    if "approved" in cd:
        track_user_activity(user_id, "applicants", "Подтверждаю ✅ (перенос встречи)")

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

        await call.message.answer("Твоя встреча была успешно перенесена! Информацию о перенесенной встрече можно "
                                  "посмотреть в разделе 'Мои встречи'")
        await bot.send_message(md[2], "Встреча была успешно перенесена")

        notif_1day_time = mddtf - timedelta(days=1)
        notif_3hours_time = mddtf - timedelta(hours=3)
        notif_1hour_time = mddtf - timedelta(hours=1)
        notif_5min_time = mddtf - timedelta(minutes=5)
        feedback_notif_time = mddtf + timedelta(hours=1)

        notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], md[0]))
        notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
        notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
        notif5 = scheduler.add_job(meeting_took_place, "date", run_date=mddtf, args=(meeting_id, md[3]))
        notif6 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(md[0],), misfire_grace_time=59)
        notif7 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(md[0],), misfire_grace_time=59)

        db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}, {notif3.id}, {notif4.id}, {notif5.id}, {notif6.id}, {notif7.id}')
    if "denied" in cd:
        track_user_activity(user_id, "applicants", "Не подтверждаю ❌ (перенос встречи)")

        db.update_meeting('status', meeting_id, "Отклонена соискателем (перенос)")
        await call.message.answer(text="Перенос встречи отменен")
        await notif_cancel_to_expert3(md[2])
        db.update_user('applicants', 'status', user_id, 'Отменил перенос последней встречи')

    logger.debug(
        f"Applicant {user_id} entered notif_reschedule_expert_result with meeting {meeting_id} and cd {cd}")


@dp.callback_query_handler(Regexp(r'^applicant_fb_agree_'))
async def applicant_fb_agree(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Оставить отзыв")

    cd = call.data
    meeting_id = cd[19:]
    db.update_meeting('applicant_fb', meeting_id, 'Ожидает отзыва')
    await call.message.answer("Напиши свою оценку эксперту (целое число от 1 до 5)")
    await call.message.edit_reply_markup()

    await state.set_state(f"applicant_writing_rating")
    async with state.proxy() as data:
        data["fb_meeting_id"] = meeting_id

    logger.debug(f"Applicant {user_id} entered applicant_fb_agree with meeting {meeting_id}")


@dp.message_handler(state="applicant_writing_rating")
async def applicant_writing_rating(message: Message, state: FSMContext):
    data = await state.get_data()
    meeting_id = data["fb_meeting_id"]

    try:
        rating = int(message.text)
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        await message.answer("Необходимо ввести число от 1 до 5 включительно. Пожалуйста, повтори попытку")
    else:
        db.update_meeting("rating", meeting_id, rating)

        expert_id = db.get_meeting(meeting_id)[2]
        expert_meetings = db.get_all_expert_meetings_with_rating(expert_id)
        expert_rating = sum([meeting[11] for meeting in expert_meetings]) / len(expert_meetings)
        db.update_user("experts", "rating", expert_id, expert_rating)

        await message.answer("Отлично! Теперь напиши свой отзыв")

        await state.set_state("applicant_writing_feedback")
        async with state.proxy() as data:
            data["fb_meeting_id"] = meeting_id

    logger.debug(f"Applicant {message.from_user.id} entered applicant_writing_rating with meeting {meeting_id}")


@dp.message_handler(state="applicant_writing_feedback")
async def applicant_writing_feedback(message: Message, state: FSMContext):
    data = await state.get_data()
    meeting_id = data["fb_meeting_id"]

    await message.answer("Спасибо за твой отзыв! Ты делаешь работу сервиса лучше.",
                         reply_markup=applicant_menu_kb)
    db.update_meeting("applicant_fb", meeting_id, message.text)

    await state.finish()

    logger.debug(f"Applicant {message.from_user.id} entered applicant_writing_feedback with meeting {meeting_id}")


@dp.callback_query_handler(text='add_photo_a')
async def add_photo(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Добавить фото к анкете")

    logger.debug(f"Applicant {user_id} entered add_photo handler")
    await call.message.edit_reply_markup()
    ad = db.get_applicant(user_id)
    photo = ad[16]
    if photo:
        await call.message.answer_photo(photo, "Твоя текущая фотография. Хочешь изменить?",
                                        reply_markup=kb2b("Изменить", "update_photo_a", "Назад", "applicant_menu"),
                                        disable_notification=True)
    else:
        await call.message.answer("У тебя пока нет фотографии. Хочешь добавить?",
                                  reply_markup=kb2b("Добавить фото", "update_photo_a", "Назад", "applicant_menu"),
                                  disable_notification=True)


@dp.callback_query_handler(text='update_photo_a')
async def update_photo(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "Добавить фото")

    logger.debug(f"Applicant {user_id} entered update_photo handler")
    await call.message.edit_reply_markup()
    await call.message.answer("Пожалуйста, пришли фотографию в чат (не файлом)",
                              disable_notification=True)
    await state.set_state('uploading_photo_a')


@dp.message_handler(state='uploading_photo_a', content_types=['photo'])
async def uploading_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id

    logger.debug(f"Applicant {user_id} entered uploading_photo handler")
    photo_id = message.photo[-1].file_id
    db.update_user('applicants', 'photo', user_id, photo_id)
    await message.answer('Твоя фотография успешно обновлена', reply_markup=applicant_menu_kb, disable_notification=True)
    await state.finish()


@dp.message_handler(state='uploading_photo_a')
async def uploading_photo_msg(message: Message, state: FSMContext):
    logger.debug(f"Applicant {message.from_user.id} entered uploading_photo_msg handler")
    await message.answer("Бот тебя не понял. Пожалуйста, пришли фото в этот чат (не ссылкой и не файлом). "
                         "Попробуй снова или вернись в главное меню.",
                         disable_notification=True,
                         reply_markup=kb2b("Добавить фото", "update_photo_a", "Назад", "applicant_menu"))
    await state.finish()


@dp.callback_query_handler(text='faq_a')
async def add_photo(call: CallbackQuery):
    user_id = call.from_user.id

    track_user_activity(user_id, "applicants", "FAQ")

    logger.debug(f"Applicant {user_id} entered faq_a handler")
    await call.message.edit_reply_markup()
    await call.message.answer("Привет! Здесь ты можешь узнать ответы на самые распространённые вопросы, а также получи"
                              "ть контакты службы поддержки. Если ты не нашёл ответ на вопрос или для его решения нужно"
                              " связаться с администраторами чат-бота и службой поддержки, пиши на почту "
                              "rosatombuddycoffee@yandex.ru\n\n"
                              "<b>1. Я не закончил заполнение профиля и хочу вернуться обратно в меню, но бот "
                              "не даёт, что делать?</b>\n "
                              "Чтобы вернуться в меню, необходимо завершить процесс регистрации. "
                              "Как только ты ответишь на все вопросы бота (это займет меньше 5-и минут), "
                              "ты сможешь изменить профиль и получить доступ к другим функциям.\n"
                              "<b>2. Бот выдаёт мне всего нескольких или даже одного соискателя/специалиста по моему "
                              "запросу.</b>\n"
                              "Такое случается. Бот подбирает собеседников по таким параметрам профиля, "
                              "как направление и желаемые темы для обсуждения. Если у тебя точечный запрос, "
                              "мы стараемся подобрать именно тех, кто обладает квалификацией по теме. "
                              "Чтобы получить больше вариантов собеседников, расширь список тем на обсуждение "
                              "через редактирование профиля в /menu.\n"
                              "<b>3. Я запланировал встречу с экспертом, мне больше не приходит никаких "
                              "оповещений</b>\n"
                              "Всё в порядке, статус встречи можно проверить по кнопке “Мои встречи”. Оповещение "
                              "придёт в случае, если один из собеседников откажется от разговора. Обрати внимание, что "
                              "все встречи планируются по московскому времени!\n"
                              "<b>4. Я пришёл на встречу, а собеседника всё нет. Куда написать?</b>\n"
                              "Первым делом проверь время. Все встречи планируются по московскому часовому поясу "
                              "(UTM +3:00). Если всё верно, а собеседник так и не появился, напиши нам на "
                              "почту или оставь обратную связь, когда её запросит бот.\n"
                              "<b>5. Бот не реагирует на нажатие кнопки</b>\n"
                              "А вот это уже нехорошо! Делай скрин (а ещё лучше видеоскриншот) и отправляй нам на "
                              "почту, контакты выше. Не забудь указать имя и @username, с которыми ты "
                              "зарегистрировался в боте.\n"
                              "<b>6. Я побывал на встрече, всё замечательно, что мне теперь делать?</b>\n"
                              "Если получены ответы на все вопросы — конечно приходить в Росатом "
                              "(актуальные вакансии тут 👉🏻 https://rosatom-career.ru/)!\nА если есть желание ещё "
                              "поговорить с кем-то, количество встреч не ограничено. Алгоритм останется прежним: "
                              "нужно начать поиск специалистов/соискателей и запланировать конференцию в "
                              "удобное время.\n"
                              "<b>7. Я хочу отменить встречу, где это сделать?</b>\n"
                              "Если по какой-то причине ты не сможешь присутствовать на встрече, зайди в "
                              "раздел “Мои встречи” и отмени запланированную конференцию.\n"
                              "<b>8. Я хочу пообщаться с собеседником по другому направлению. Что нужно "
                              "сделать, чтобы расширить или полностью изменить подборку?</b>\n"
                              "Для этого нужно зайти в меню /menu и отредактировать профиль: выбрать"
                              " другое направление и расширить список тем для обсуждения.\n"
                              "<b>9. Могу ли я общаться не по видео, а в чате? </b>\n"
                              "Сейчас в нашем боте возможно только планирование конференций. Однако если вы захотите "
                              "всё же связаться с собеседником другим способом, напишите нам на почту. Для такого"
                              " запроса сделайте скриншот профиля собеседника, который вам интересен. "
                              "Мы пришлём контакты ответным письмом.",
                              reply_markup=kb1b("Назад", "applicant_menu"),
                              disable_notification=True)


@dp.callback_query_handler(text='change_agreement_to_show_contacts_a')
async def change_agreement_to_show_contacts(call: CallbackQuery):
    applicant_id = call.from_user.id
    applicant_agree_to_show_contacts = db.get_applicant(applicant_id)[18]
    if applicant_agree_to_show_contacts:
        text = f"Нажми \"Нет\", если ты не хочешь, чтобы тебе писали эксперты в телеграм (@{call.from_user.username})"
        kb = kb2b("Нет", "change_agreement_a", "Назад", "expert_menu")
    else:
        text = "Нажми \"Да\", чтобы мы могли показывать твои контактные данные в телеграм " \
               f"(@{call.from_user.username}) экспертам. Так они смогут связаться с тобой, если " \
               "проблема с конференцией"
        kb = kb2b("Да", "change_agreement_a", "Назад", "expert_menu")

    await call.message.edit_reply_markup()
    await call.message.answer(text, reply_markup=kb)

    logger.debug(f"Expert {applicant_id} entered change_agreement_to_show_contacts")


@dp.callback_query_handler(text='change_agreement_a')
async def proceed_changing_agreement_to_show_contacts(call: CallbackQuery):
    applicant_id = call.from_user.id
    applicant_agree_to_show_contacts = db.get_applicant(applicant_id)[18]
    if applicant_agree_to_show_contacts:
        new_agreement_status = False
    else:
        new_agreement_status = True

    db.update_user('applicants', 'agree_to_show_contacts', applicant_id, new_agreement_status)

    await call.message.edit_reply_markup()
    await call.message.answer("Статус согласия был успешно изменен", reply_markup=applicant_menu_kb)

    logger.debug(f"Applicant {applicant_id} entered proceed_changing_agreement_to_show_contacts")
