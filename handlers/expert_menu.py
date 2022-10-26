import re
from datetime import datetime, timedelta

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import Message, CallbackQuery

from handlers.notifications import notif_cancel_to_applicant, notif_1day, \
    notif_3hours, notif_cancel_to_applicant2, notif_after_show_contacts, notif_1hour, notif_5min, \
    feedback_notif_applicant, feedback_notif_expert
from keyboards import expert_menu_kb, kb1b, kb3b, suitable_applicants_kb2, kb2b, meetings_e_kb, \
    slots_kb
from loader import bot, dp, db, scheduler
from my_logger import logger
from zoom import create_meeting


@dp.callback_query_handler(text='expert_menu')
async def expert_menu(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer(text="Вы в главном меню. Если захотите сюда вернуться, используйте команду /menu",
                              reply_markup=expert_menu_kb,
                              disable_notification=True)
    logger.debug(f"Expert {call.from_user.id} entered expert_menu handler")


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
    logger.debug(f"Expert {call.from_user.id} entered search_applicants handler")
    await call.message.edit_reply_markup()
    suitable_applicants = search_applicant(call.from_user.id)
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
        logger.debug(f"Expert {call.from_user.id} entered search_applicants handler but don't "
                     f"have any suitable applicants")


@dp.callback_query_handler(Regexp(r'^sakbp_'))
async def page_click_expert(call: CallbackQuery):
    suitable_applicants = search_applicant(call.from_user.id)
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
    logger.debug(f"Expert {call.from_user.id} entered page_click_expert handler with page {page}")


@dp.callback_query_handler(Regexp(r'^forma_'))
async def choosing_applicant(call: CallbackQuery):
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
    logger.debug(f"Expert {call.from_user.id} entered choosing_applicant handler with applicant {applicant_id}")


@dp.callback_query_handler(Regexp(r'^choosea_'))
async def applicant_chosen(call: CallbackQuery):
    applicant_id = call.data[8:]

    await call.message.edit_reply_markup()
    await call.message.answer(text="Выбери подходящий пункт",
                              reply_markup=kb3b("Отправить приглашение соискателю",
                                                f"send_free_slots_{applicant_id}_init_by_expert",
                                                "Показать контакты", f"show_contacts_a_{applicant_id}",
                                                "Назад", f"forma_{applicant_id}"),
                              disable_notification=True)

    logger.debug(f"Expert {call.from_user.id} entered applicant_chosen handler "
                 f"with applicant {applicant_id}")


@dp.callback_query_handler(Regexp(r'^send_free_slots_'))
async def send_free_slots(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите временные слоты, когда вам удобно провести встречу, "
                              "желательно указать несколько. <b>Укажите московское время</b>\n\n"
                              "<i>Формат:\n"
                              "25.01.2022 17:00, 27.01.2022 12:30, "
                              "28.01.2022 10:00, 31.01.2022 10:45, 02.02.2022 16:15</i>")

    await state.set_state('input_slots')
    async with state.proxy() as data:
        call_data_list = call.data.split("_")

        data["applicant_id"] = int(call_data_list[3])
        data["init_by"] = call_data_list[6]

    logger.debug(f"Expert {call.from_user.id} entered send_free_slots handler")


@dp.message_handler(state='input_slots')
async def notify_applicant_about_slots(message: Message, state: FSMContext):
    async with state.proxy() as data:
        applicant_id = data["applicant_id"]
        init_by = data["init_by"]

    text = message.text
    try:
        slots_list = text.split(',')
        slots_list = [slot.lstrip().rstrip() for slot in slots_list]
        esl = []
        for slot in slots_list:
            if not re.match("^\d{1,2}\.\d{1,2}\.\d{4} \d{1,2}:\d{1,2}$", slot):
                await message.answer(text=f'Бот не смог распознать следующий слот: <i>{slot}</i>\n\n'
                                          'Пожалуйста, придерживайтесь формата. Отправьте временные слоты еще раз',
                                     disable_notification=True)
                await state.set_state('input_slots')
                logger.debug(
                    f"Expert {message.from_user.id} entered notify_applicant_about_slots handler but write incorrect slot: {slot}")

                return

            if datetime.strptime(slot, '%d.%m.%Y %H:%M') > datetime.today():
                esl.append(slot)

        if esl:
            ed = db.get_expert(message.from_user.id)

            if ed[7]:
                division = ed[7]
            else:
                division = ed[8]

            text = f"Эксперт {ed[5]} отправил тебе временные слоты, " \
                   "когда он может провести конференцию. Выбери один из них\n\n" \
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
                                         reply_markup=slots_kb(message.from_user.id, init_by, esl))
                else:
                    await bot.send_photo(applicant_id, photo=ed[15])
                    await bot.send_message(applicant_id,
                                           text=text,
                                           reply_markup=slots_kb(message.from_user.id, init_by, esl),
                                           disable_notification=True)
            else:
                await bot.send_message(applicant_id,
                                       text=text,
                                       reply_markup=slots_kb(message.from_user.id, init_by, esl),
                                       disable_notification=True)

            await message.answer(text="Слоты были отправлены выбранному соискателю. "
                                      "Оставайтесь на связи, мы сообщим вам о выборе соискателя и дальнейшую "
                                      "информацию о встрече, если она будет подтверждена",
                                 reply_markup=kb1b('Вернуться в главное меню', 'expert_menu'),
                                 disable_notification=True)
            await state.finish()

            logger.debug(
                f"Expert {message.from_user.id} entered notify_applicant_about_slots handler and sent slots to applicant {applicant_id}")
        else:
            logger.warning(
                f"Expert {message.from_user.id} entered notify_applicant_about_slots handler but slots is overdue")
            await message.answer(text='Ни один из введенных Вами слотов не является действующим. '
                                      'Отправьте временные слоты еще раз',
                                 disable_notification=True)
            await state.set_state('input_slots')

    except Exception as e:
        logger.warning(
            f"Expert {message.from_user.id} entered notify_applicant_about_slots handler but got an error: {e}")
        await message.answer(text=f'Бот не смог распознать ваш ответ\n\n'
                                  f'Пожалуйста, придерживайтесь формата. Отправьте временные слоты еще раз',
                             disable_notification=True)
        await state.set_state('input_slots')


@dp.callback_query_handler(text='expert_meetings')
async def expert_meetings(call: CallbackQuery):
    await call.message.edit_reply_markup()
    em = db.get_expert_meetings(call.from_user.id)
    if em:
        await call.message.answer(text="Ваш список встреч (время по МСК)",
                                  reply_markup=meetings_e_kb(em),
                                  disable_notification=True)
        logger.debug(f"Expert {call.from_user.id} entered exert_meetings handler and got {len(em)} his meetings")
    else:
        await call.message.answer(text="У вас пока нет запланированных встреч",
                                  reply_markup=kb1b("Назад", "expert_menu"),
                                  disable_notification=True)
        logger.debug(f"Expert {call.from_user.id} entered exert_meetings handler but he doesn't have meetings yet")


@dp.callback_query_handler(Regexp(r'^show_contacts_a_'))
async def show_contacts_a(call: CallbackQuery):
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
    scheduler.add_job(notif_after_show_contacts, "date", run_date=notif_date, args=(call.from_user.id, applicant_id,))

    logger.debug(f"Expert {call.from_user.id} entered show_contacts handler")


@dp.callback_query_handler(Regexp(r'^mkbp_e_'))
async def expert_chosen(call: CallbackQuery):
    page = int(call.data[7:])
    em = db.get_expert_meetings(call.from_user.id)
    await call.message.edit_reply_markup(meetings_e_kb(em, page))
    logger.debug(f"Expert {call.from_user.id} entered expert_chosen handler with page {page}")


@dp.callback_query_handler(Regexp(r'^meeting_e_'))
async def check_meeting(call: CallbackQuery):
    meeting_id = int(call.data[10:])
    md = db.get_meeting(meeting_id)  # meeting's data
    ad = db.get_applicant(md[3])  # applicant's data
    await call.message.answer(text=f"Информация о встрече\n\n"
                                   f"<b>Соискатель:</b> {ad[5]} \n"
                                   f"<b>Дата и время по МСК:</b> {md[4]}\n",
                              reply_markup=kb2b("Отменить встречу", f'cancel_meeting_e_{md[0]}',
                                                "Назад", f'expert_meetings'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Expert {call.from_user.id} entered check_meeting handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^cancel_meeting_e_'))
async def meeting_cancelation(call: CallbackQuery):
    await call.message.edit_reply_markup()
    meeting_id = int(call.data[17:])
    md = db.get_meeting(meeting_id)
    applicant_id = md[3]
    meeting_date = md[4]
    expert_name = db.get_expert(call.from_user.id)[5]
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
    logger.debug(f"Expert {call.from_user.id} entered meeting_cancelation handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^denied_e'))
@dp.callback_query_handler(Regexp(r'^approved_e'))
async def notif_init_applicant_result(call: CallbackQuery):
    await call.message.edit_reply_markup()

    cd = call.data
    if "approved" in cd:
        meeting_id = int(cd[11:])
        md = db.get_meeting(meeting_id)

        db.update_meeting('status', meeting_id, "Подтверждена")
        db.update_user('applicants', 'status', md[3], 'Встреча подтверждена')

        mddtf = datetime.strptime(md[4], '%d.%m.%Y %H:%M')  # meeting date in datetime format

        scheduler.add_job(meeting_took_place, "date", run_date=mddtf, args=(meeting_id, call.from_user.id,))

        local_now = datetime.now()
        now = local_now.astimezone(pytz.timezone('Europe/Moscow')).replace(tzinfo=None)

        hours_left_before_meeting = (mddtf - now).seconds / 3600
        if hours_left_before_meeting > 3:
            notif_1day_time = mddtf - timedelta(days=1)
            notif_3hours_time = mddtf - timedelta(hours=3)

            notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
            notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], md[0]))

            db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}')
            await call.message.answer(text="Встреча подтверждена")
        else:
            mdzf = datetime.strptime(md[4], '%d.%m.%Y %H:%M').strftime(
                '%Y-%m-%dT%H:%M:%S')  # meeting date in zoom format
            link = create_meeting(mdzf)

            db.update_user('applicants', 'status', md[3], 'Последняя встреча состоялась')

            await call.message.answer(text="Уже менее чем через 3 часа у Вас запланирована встреча.\n\n"
                                           f"Ссылка: {link}")
            await bot.send_message(md[3], text=f"Хорошей встречи! Мы будем тебя ждать: {link}")

            notif_1hour_time = mddtf - timedelta(hours=1)
            notif_5min_time = mddtf - timedelta(minutes=5)
            feedback_notif_time = mddtf + timedelta(days=1)

            notif1 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
            notif2 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
            notif3 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(md[0],))
            notif4 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(md[0],))

            db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}, {notif3.id}, {notif4.id}')

        logger.debug(
            f"Expert {call.from_user.id} entered notif_init_applicant_result with meeting {meeting_id} and cd {cd}")
    if "denied" in cd:
        meeting_id = cd[9:]
        md = db.get_meeting(meeting_id)
        db.update_meeting('status', meeting_id, "Отклонена экспертом")
        await call.message.answer(text="Встреча отменена.")
        db.update_user('applicants', 'status', md[3], 'Эксперт отменил последнюю встречу')
        await notif_cancel_to_applicant2(md[3])
        logger.debug(
            f"Expert {call.from_user.id} entered notif_init_applicant_result with meeting {meeting_id} and cd {cd}")


def meeting_took_place(meeting_id, user_id):
    meeting_ids = [meeting[0] for meeting in db.get_expert_meetings(user_id)]

    if meeting_id in meeting_ids:
        db.update_meeting("status", meeting_id, 'Состоялась')


@dp.callback_query_handler(Regexp(r'^expert_fb_agree_'))
async def expert_fb_agree(call: CallbackQuery, state: FSMContext):
    cd = call.data
    meeting_id = cd[16:]
    db.update_meeting('expert_fb', meeting_id, 'Ожидает отзыва')
    await call.message.answer("Напишите ваш отзыв в ответом письме:")
    await state.set_state(f"expert_writing_feedback")
    await call.message.edit_reply_markup()
    logger.debug(f"Expert {call.from_user.id} entered expert_fb_agree with meeting {meeting_id}")


@dp.message_handler(state="expert_writing_feedback")
async def expert_writing_feedback(message: Message, state: FSMContext):
    fb = message.text
    meeting_id = db.get_meeting_fb_e()[0]  # really weak implementation, can cause errors
    await message.answer("Спасибо за ваш отзыв! Вы делаете работу сервиса лучше.",
                         reply_markup=expert_menu_kb)
    db.update_meeting("expert_fb", meeting_id, fb)
    await state.finish()
    logger.debug(f"Expert {message.from_user.id} entered expert_writing_feedback with meeting {meeting_id}")


@dp.callback_query_handler(text='add_photo_e')
async def add_photo(call: CallbackQuery):
    logger.debug(f"Expert {call.from_user.id} entered add_photo handler")
    await call.message.edit_reply_markup()
    ed = db.get_expert(call.from_user.id)
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
    logger.debug(f"Expert {call.from_user.id} entered update_photo handler")
    await call.message.edit_reply_markup()
    await call.message.answer("Пожалуйста, пришлите фотографию в чат (не файлом)",
                              disable_notification=True)
    await state.set_state('uploading_photo_e')


@dp.message_handler(state='uploading_photo_e', content_types=['photo'])
async def uploading_photo(message: Message, state: FSMContext):
    logger.debug(f"Expert {message.from_user.id} entered uploading_photo handler")
    photo_id = message.photo[-1].file_id
    db.update_user('experts', 'photo', message.from_user.id, photo_id)
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
