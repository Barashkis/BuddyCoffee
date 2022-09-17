import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import CallbackQuery, Message
from datetime import datetime, timedelta
from config import directions_list, divisions_list
from handlers.notifications import notif_init_expert, notif_approved_3hours_to_expert, \
    notif_cancel_to_expert, notif_cancel_to_expert2, notif_3hours, notif_1day, notif_5min, notif_1hour, \
    feedback_notif_applicant, feedback_notif_expert
from keyboards import applicant_menu_kb, kb1b, suitable_experts_kb, kb2b, slots_a_kb, choosing_time_a_cd, meetings_a_kb, \
    suitable_experts_kb2
from loader import dp, db, scheduler
import pytz
import re

from my_logger import logger
from zoom import create_meeting


@dp.callback_query_handler(text='applicant_menu')
async def applicant_menu(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer(text="Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu",
                              reply_markup=applicant_menu_kb,
                              disable_notification=True)
    logger.debug(f"Applicant {call.from_user.id} entered applicant_menu handler")


def search_expert(applicant_id):
    applicant_data = db.get_applicant(applicant_id)
    applicant_topics = applicant_data[13].split(', ')
    experts = db.get_experts()
    suitable_experts = []
    for expert in experts:
        if expert[12] is not None:
            if any(topic in expert[12].split(', ')  for topic in applicant_topics):
                if any(datetime.strptime(slot.lstrip().rstrip().replace('\n', ''), '%d.%m.%Y %H:%M') > datetime.today() for slot in expert[11].split(',')):
                    suitable_experts.append({'user_id': expert[0], 'fullname': expert[5]})
    logger.debug(f"Search_expert function shows that expert {applicant_id} have "
                 f"{len(suitable_experts)} suitable experts")
    return suitable_experts

@dp.callback_query_handler(text='search_experts')
async def search_experts(call: CallbackQuery):
    logger.debug(f"Applicant {call.from_user.id} entered search_experts handler")
    suitable_experts = search_expert(call.from_user.id)
    if suitable_experts:
        expert_id = suitable_experts[0].get("user_id")
        ed = db.get_expert(expert_id)
        if ed[7]:
            division = divisions_list.get(int(ed[7]))
        else:
            division = ed[8]
        if ed[15]:
            await call.message.answer_photo(ed[15],
                                            caption=f"<b>Имя:</b> {ed[5]}\n"
                                            f"<b>Направление:</b> {directions_list.get(int(ed[6]))}\n"
                                            f"<b>Дивизион:</b> {division}\n"
                                            f"<b>Экспертный профиль:</b> {ed[10]}\n",
                                            reply_markup=suitable_experts_kb2(suitable_experts),
                                            disable_notification=True)
        else:
            await call.message.answer(f"<b>Имя:</b> {ed[5]}\n"
                                      f"<b>Направление:</b> {directions_list.get(int(ed[6]))}\n"
                                      f"<b>Дивизион:</b> {division}\n"
                                      f"<b>Экспертный профиль:</b> {ed[10]}\n",
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
        logger.debug(f"Applicant {call.from_user.id} entered search_experts handler but don't "
                     f"have any suitable applicants")
        await call.message.edit_reply_markup()


@dp.callback_query_handler(Regexp(r'^sekbp_'))
async def page_click_applicant(call: CallbackQuery):
    suitable_experts = search_expert(call.from_user.id)
    page = int(call.data[6:])
    expert_id = suitable_experts[page-1].get("user_id")
    ed = db.get_expert(expert_id)
    if ed[7]:
        division = divisions_list.get(int(ed[7]))
    else:
        division = ed[8]
    if ed[15]:
        await call.message.answer_photo(ed[15],
                                        caption=f"<b>Имя:</b> {ed[5]}\n"
                                                f"<b>Направление:</b> {directions_list.get(int(ed[6]))}\n"
                                                f"<b>Дивизион:</b> {division}\n"
                                                f"<b>Экспертный профиль:</b> {ed[10]}\n",
                                        reply_markup=suitable_experts_kb2(suitable_experts, page),
                                        disable_notification=True)
    else:
        await call.message.answer(f"<b>Имя:</b> {ed[5]}\n"
                                  f"<b>Направление:</b> {directions_list.get(int(ed[6]))}\n"
                                  f"<b>Дивизион:</b> {division}\n"
                                  f"<b>Экспертный профиль:</b> {ed[10]}\n",
                                  reply_markup=suitable_experts_kb2(suitable_experts, page),
                                  disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {call.from_user.id} entered page_click_applicant handler with page {page}")


@dp.callback_query_handler(Regexp(r'^forme_'))
async def choosing_expert(call: CallbackQuery):
    expert_id = int(call.data[6:])
    ed = db.get_expert(expert_id)
    if ed[7]:
        division = divisions_list.get(int(ed[7]))
    else:
        division = ed[8]
    await call.message.answer(text=f"<b>Имя:</b> {ed[5]}\n"
                                   f"<b>Направление:</b> {directions_list.get(int(ed[6]))}\n"
                                   f"<b>Дивизион:</b> {division}\n"
                                   f"<b>Экспертный профиль:</b> {ed[10]}\n",
                              reply_markup=kb2b("Выбрать специалиста", f'choosee_{expert_id}',
                                                "Назад", f'search_experts'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {call.from_user.id} entered choosing_expert handler with applicant {expert_id}")



@dp.callback_query_handler(Regexp(r'^choosee_'))
async def expert_chosen(call: CallbackQuery):
    cd = call.data
    expert_id = int(cd[8:])
    ed = db.get_expert(expert_id)
    slots_raw = ed[11].split(', ')
    slots = []
    for slot in slots_raw:
        if datetime.strptime(slot, '%d.%m.%Y %H:%M') > datetime.today():
            slots.append(slot)
    await call.message.answer(text="Выбери подходящий слот. <b>В слотах указано московское время</b>",
                              reply_markup=slots_a_kb(expert_id, slots),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {call.from_user.id} entered expert_chosen handler "
                 f"with applicant {expert_id} and {len(slots)} free slots")


@dp.callback_query_handler(Regexp(r'^skbp_'))  # words both for applicant's menu and expert's menu
async def expert_chosen(call: CallbackQuery):
    expert_id = int(re.split('_', call.data)[1])
    slots = db.get_expert(expert_id)[11].split(', ')
    page = int(re.split('_', call.data)[2])
    await call.message.edit_reply_markup(slots_a_kb(expert_id, slots, page))
    logger.debug(f"User {call.from_user.id} entered expert_chosen handler with page {page}")


@dp.callback_query_handler(choosing_time_a_cd.filter())
async def choosing_time(call: CallbackQuery, callback_data: dict):
    await call.message.edit_reply_markup()
    expert_id = callback_data.get('expert_id')
    applicant_id = call.from_user.id
    applicant_name = db.get_applicant(applicant_id)[5]
    n_slot = int(callback_data.get('slot'))  # slot number
    experts_slots = db.get_expert(expert_id)[11]
    slots_raw = experts_slots.split(', ')
    esl = []
    for slot in slots_raw:
        if datetime.strptime(slot, '%d.%m.%Y %H:%M') > datetime.today():
            esl.append(slot)
    slot = esl[n_slot]
    td = datetime.now(tz=pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y')
    db.add_meeting(td, expert_id, applicant_id, slot, 'Инициирована соискателем')
    meeting_id = db.get_last_insert_meeting_id(expert_id, applicant_id)[0]
    await call.message.answer(text="Отличный выбор! Оставайся на связи, мы напомним тебе о встрече! "
                                   "Если хочешь перенести или отменить встречу, выбери пункт в меню 'Мои встречи'",
                              reply_markup=kb1b('Вернуться в главное меню', 'applicant_menu'),
                              disable_notification=True)
    db.update_user('applicants', 'status', call.from_user.id, 'Инициировал встречу')
    await notif_init_expert(expert_id, slot, applicant_name, meeting_id)
    logger.debug(f"Applicant {call.from_user.id} entered choosing_time handler "
                 f"with expert {expert_id} and {slot} slot")

@dp.callback_query_handler(text='applicant_meetings')
async def applicant_meetings(call: CallbackQuery):
    await call.message.edit_reply_markup()
    am = db.get_applicant_meetings(call.from_user.id)
    if am:
        await call.message.answer(text="Ваш список встреч. <b>Указано московское время</b>",
                                  reply_markup=meetings_a_kb(am),
                                  disable_notification=True)
        logger.debug(f"Applicant {call.from_user.id} entered applicant_meetings handler and got {len(am)} his meetings")
    else:
        await call.message.answer(text="У тебя пока нет запланированных встреч",
                                  reply_markup=kb1b("Назад", "applicant_menu"),
                                  disable_notification=True)
    logger.debug(f"Applicant {call.from_user.id} entered applicant_meetings handler but he doesn't have meetings yet")


@dp.callback_query_handler(Regexp(r'^show_contacts_a_'))
async def show_contacts_a(call: CallbackQuery):
    db.update_stat("applicants")

    expert_id = int(call.data[16:])
    ed = db.get_expert(expert_id)

    await call.answer()
    await call.message.answer(f"Если по каким-то причинам ты хочешь связаться с экспертом лично, вот его контакты - @{ed[2]}. "
                              "Обрати внимание, если ты видишь @None вместо контакта, значит, с этим пользователем "
                              "можно связаться, только запланировав встречу в нашем боте")
    logger.debug(f"Applicant {call.from_user.id} entered show_contacts handler")


@dp.callback_query_handler(Regexp(r'^mkbp_a_'))
async def expert_chosen(call: CallbackQuery):
    page = int(call.data[7:])
    am = db.get_applicant_meetings(call.from_user.id)
    await call.message.edit_reply_markup(meetings_a_kb(am, page))
    logger.debug(f"Applicant {call.from_user.id} entered expert_chosen handler with page {page}")


@dp.callback_query_handler(Regexp(r'^meeting_a_'))
async def check_meeting(call: CallbackQuery):
    meeting_id = int(call.data[10:])
    print(meeting_id)
    md = db.get_meeting(meeting_id)  # meeting's data
    ed = db.get_expert(md[2])  # expert's data
    await call.message.answer(text=f"Информация о встрече\n\n"
                                   f"<b>Специалист:</b> {ed[5]} \n"
                                   f"<b>Дата и время по МСК:</b> {md[4]}\n",
                              reply_markup=kb2b("Отменить встречу", f'cancel_meeting_a_{md[0]}',
                                                "Назад", f'applicant_meetings'),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {call.from_user.id} entered check_meeting handler with meeting {meeting_id}")



@dp.callback_query_handler(Regexp(r'^cancel_meeting_a_'))
async def meeting_cancelation(call: CallbackQuery):
    meeting_id = int(call.data[17:])
    md = db.get_meeting(meeting_id)
    expert_id = md[2]
    meeting_date = md[4]
    applicant_name = db.get_applicant(call.from_user.id)[5]
    await call.message.answer(text="Встреча отменена.",
                              reply_markup=kb1b("Назад", "applicant_menu"))
    db.update_meeting('status', meeting_id, 'Отменена соискателем')
    db.update_user('applicants', 'status', call.from_user.id, 'Отменил последнюю встречу')
    await notif_cancel_to_expert(expert_id, meeting_date, applicant_name)
    if md[9] is not None:
        mjl = md[9].split(', ')  # meeting jobs list
        for job in mjl:
            try:
                db.remove_job(job)
                logger.debug(f"Job {job} was removed from job storage")
            except Exception as e:
                logging.warning(f"Job {job} from meeting {meeting_id} was not deleted: {e}")
    logger.debug(f"Applicant {call.from_user.id} entered meeting_cancelation handler with meeting {meeting_id}")



@dp.callback_query_handler(Regexp(r'^denied_a_'))
@dp.callback_query_handler(Regexp(r'^approved_a_'))
async def notif_init_expert_result(call: CallbackQuery):
    cd = call.data
    if "approved" in cd:
        meeting_id = cd[11:]
        md = db.get_meeting(meeting_id)
        mddtf = datetime.strptime(md[4], '%d.%m.%Y %H:%M')  # meeting date in datetime format
        notif_1day_time = mddtf - timedelta(days=1)
        notif_3hours_time = mddtf - timedelta(hours=3)
        db.update_meeting('status', meeting_id, "Подтверждена")
        await call.message.answer(text="Встреча подтверждена.")
        db.update_user('applicants', 'status', call.from_user.id, 'Встреча подтверждена')
        notif1 = scheduler.add_job(notif_1day, "date", run_date=notif_1day_time, args=(md[3],))
        notif2 = scheduler.add_job(notif_3hours, "date", run_date=notif_3hours_time, args=(md[3], md[0]))
        db.update_meeting('notifications_ids', meeting_id, f'{notif1.id}, {notif2.id}')
        await call.message.edit_reply_markup()
        logger.debug(f"Applicant {call.from_user.id} entered notif_init_expert_result with meeting {meeting_id} and cd {cd}")
    if "denied" in cd:
        meeting_id = cd[9:]
        md = db.get_meeting(meeting_id)
        db.update_meeting('status', meeting_id, "Отклонена соискателем")
        await call.message.answer(text="Встреча отменена.")
        await notif_cancel_to_expert2(md[2])
        await call.message.edit_reply_markup()
        db.update_user('applicants', 'status', call.from_user.id, 'Отменил последнюю встречу')
        logger.debug(f"Applicant {call.from_user.id} entered notif_init_expert_result with meeting {meeting_id} and cd {cd}")


@dp.callback_query_handler(Regexp(r'^approved_3hours_'))
async def approved_3hours(call: CallbackQuery):
    cd = call.data
    meeting_id = cd[16:]
    md = db.get_meeting(meeting_id)

    mdzf = datetime.strptime(md[4], '%d.%m.%Y %H:%M').strftime('%Y-%m-%dT%H:%M:%S')  # meeting date in zoom format
    db.update_meeting("status", meeting_id, 'Состоялась')
    db.update_user('applicants', 'status', call.from_user.id, 'Последняя встреча состоялась')
    link = create_meeting(mdzf)
    await call.message.answer(text=f"Хорошей встречи! Мы будем тебя ждать: {link}")
    await notif_approved_3hours_to_expert(md[2], link)
    await call.message.edit_reply_markup()

    md = db.get_meeting(meeting_id)
    mddtf = datetime.strptime(md[4], '%d.%m.%Y %H:%M')  # meeting date in datetime format
    notif_1hour_time = mddtf - timedelta(hours=1)
    notif_5min_time = mddtf - timedelta(minutes=5)
    feedback_notif_time = mddtf + timedelta(days=1)
    notif3 = scheduler.add_job(notif_1hour, "date", run_date=notif_1hour_time, args=(md[3],))
    notif4 = scheduler.add_job(notif_5min, "date", run_date=notif_5min_time, args=(md[3],))
    notif5 = scheduler.add_job(feedback_notif_applicant, "date", run_date=feedback_notif_time, args=(md[0],))
    notif6 = scheduler.add_job(feedback_notif_expert, "date", run_date=feedback_notif_time, args=(md[0],))
    db.update_meeting('notifications_ids', meeting_id, f'{notif3.id}, {notif4.id}, {notif5.id}, {notif6.id}')
    logger.debug(f"Applicant {call.from_user.id} entered approved_3hours handler with meeting {meeting_id}")


@dp.callback_query_handler(Regexp(r'^cancel_3hours_'))
async def canceled_3hours(call: CallbackQuery):
    cd = call.data
    meeting_id = cd[14:]
    md = db.get_meeting(meeting_id)
    db.update_meeting("status", meeting_id, 'Отменена')
    db.update_user('applicants', 'status', call.from_user.id, 'Отменил последнюю встречу')
    await call.message.answer(text="Встреча отменена",
                              reply_markup=applicant_menu_kb,
                              disable_notification=True)
    await notif_cancel_to_expert2(md[2])
    await call.message.edit_reply_markup()
    if md[9] is not None:
        mjl = md[9].split(', ')  # meeting jobs list
        for job in mjl:
            try:
                db.remove_job(job)
                logger.debug(f"Job {job} was removed from job storage")
            except Exception as e:
                logging.warning(f"Job {job} from meeting {meeting_id} was not deleted: {e}")
    logger.debug(f"Applicant {call.from_user.id} entered canceled_3hours handler with meeting {meeting_id}")



@dp.callback_query_handler(Regexp(r'^applicant_fb_agree_'))
async def applicant_fb_agree(call: CallbackQuery, state: FSMContext):
    cd = call.data
    meeting_id = cd[19:]
    db.update_meeting('applicant_fb', meeting_id, 'Ожидает отзыва')
    await call.message.answer("Напиши свой отзыв в ответом письме:")
    await state.set_state(f"applicant_writing_feedback")
    await call.message.edit_reply_markup()
    logger.debug(f"Applicant {call.from_user.id} entered applicant_fb_agree with meeting {meeting_id}")



@dp.message_handler(state="applicant_writing_feedback")
async def applicant_writing_feedback(message: Message, state: FSMContext):
    fb = message.text
    meeting_id = db.get_meeting_fb_a()[0]  # really weak implementation, can cause errors
    await message.answer("Спасибо за твой отзыв! Ты делаешь работу сервиса лучше.",
                         reply_markup=applicant_menu_kb)
    db.update_meeting("applicant_fb", meeting_id, fb)
    await state.finish()
    logger.debug(f"Applicant {message.from_user.id} entered applicant_writing_feedback with meeting {meeting_id}")


@dp.callback_query_handler(text='add_photo_a')
async def add_photo(call: CallbackQuery):
    logger.debug(f"Applicant {call.from_user.id} entered add_photo handler")
    await call.message.edit_reply_markup()
    ad = db.get_applicant(call.from_user.id)
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
    logger.debug(f"Applicant {call.from_user.id} entered update_photo handler")
    await call.message.edit_reply_markup()
    await call.message.answer("Пожалуйста, пришли фотографию в чат (не файлом)",
                              disable_notification=True)
    await state.set_state('uploading_photo_a')


@dp.message_handler(state='uploading_photo_a', content_types=['photo'])
async def uploading_photo(message: Message, state: FSMContext):
    logger.debug(f"Applicant {message.from_user.id} entered uploading_photo handler")
    photo_id = message.photo[-1].file_id
    db.update_user('applicants', 'photo', message.from_user.id, photo_id)
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
    logger.debug(f"Applicant {call.from_user.id} entered faq_a handler")
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