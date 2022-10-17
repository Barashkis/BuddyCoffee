from aiogram.dispatcher.filters import Regexp
from aiogram.types import CallbackQuery

from keyboards import kb2b
from loader import dp, db
from my_logger import logger


async def notif_cancel_to_expert2(expert_id):
    await dp.bot.send_message(expert_id, text=f'К сожалению, соискатель отказался от встречи. По кнопке '
                                              f'"Посмотреть анкеты соискателей" можно выбрать другого соискателя')
    logger.debug(f'Expert {expert_id} got notif_cancel_to_expert2 notification')


async def notif_cancel_to_applicant(applicant_id, meeting_date, expert_name):
    await dp.bot.send_message(applicant_id, text=f'{expert_name} отменил встречу, назначенную {meeting_date}')
    logger.debug(f'Applicant {applicant_id} got notif_cancel_to_applicant notification of {meeting_date} meeting')


async def notif_cancel_to_applicant2(applicant_id):
    await dp.bot.send_message(applicant_id, text=f'К сожалению, текущий график выбранного эксперта перегружен. '
                                                 f'Давай попробуем выбрать другого эксперта?')
    logger.debug(f'Applicant {applicant_id} got notif_cancel_to_applicant2 notification')


async def notif_approved_3hours_to_expert(expert_id, link):
    await dp.bot.send_message(expert_id, text=f'Напоминаем о том, что через 3 часа у вас запланирована встреча.\n\n'
                                              f'Ссылка: {link}')
    logger.debug(f'Expert {expert_id} got notif_approved_3hours_to_expert notification')


async def notif_init_applicant(applicant_id, slot, expert_fullname, meeting_id):
    await dp.bot.send_message(applicant_id, text=f'Специалист {expert_fullname} назначил вам встречу {slot}. <b>Указано московское время</b> '
                                                 f'Вы подтверждаете ее?',
                              reply_markup=kb2b("Подтверждаю ✅", f'approved_a_{meeting_id}',
                                                "Не подтверждаю ❌", f"denied_a_{meeting_id}"))
    logger.debug(f'Applicant {applicant_id} got notif_init_applicant notification')



async def notif_cancel_3hours_to_expert(expert_id):
    await dp.bot.send_message(expert_id, text=f'К сожалению, соискатель отказался от встречи. По кнопке "Посмотреть '
                                              f'анкеты соискателей" можно выбрать другого соискателя')
    logger.debug(f'Expert {expert_id} got notif_cancel_3hours_to_expert notification')


async def notif_1day(applicant_id):
    await dp.bot.send_message(applicant_id,
                              text="Напоминаем о запланированной встрече. Подробности о встрече ты можешь "
                                   "узнать в меню 'Мои встречи'. За 3 часа до встречи мы отправим "
                                   "уведомление, на которое нужно будет оперативно откликнуться и "
                                   "подтвердить или отклонить готовность присутствовать на встрече.")
    logger.debug(f'Applicant {applicant_id} got notif_1day notification')


async def notif_3hours(applicant_id, meeting_id):
    await dp.bot.send_message(applicant_id, text="Пожалуйста, подтверди возможность присутствовать на встрече!",
                              reply_markup=kb2b("Подтверждаю", f"approved_3hours_{meeting_id}",
                                                "Отменить встречу", f"cancel_3hours_{meeting_id}"))
    logger.debug(f'Applicant {applicant_id} got notif_3hours notification about {meeting_id} meeting')


async def notif_1hour(applicant_id):
    await dp.bot.send_message(applicant_id, text="Твоя консультация состоится уже через час!")
    logger.debug(f'Applicant {applicant_id} got notif_1hour notification')


async def notif_5min(applicant_id):
    await dp.bot.send_message(applicant_id, text="До начала консультации осталось 5 минут!")
    logger.debug(f'Applicant {applicant_id} got notif_5min notification')


async def notif_cancel_to_expert(expert_id, meeting_date, applicant_name):
    await dp.bot.send_message(expert_id, text=f'{applicant_name} отменил встречу, назначенную {meeting_date}')
    logger.debug(f'Expert {expert_id} got notif_cancel_to_expert notification about {meeting_date} meeting')


async def notif_init_expert(expert_id, slot, applicant_name, meeting_id):
    await dp.bot.send_message(expert_id, text=f'Соискатель {applicant_name} назначил вам встречу {slot}. <b>Указано московское время</b>. '
                                              f'Вы подтверждаете ее?',
                              reply_markup=kb2b("Подтверждаю ✅", f'approved_e_{meeting_id}',
                                                "Не подтверждаю ❌", f"denied_e_{meeting_id}"))
    logger.debug(f'Expert {expert_id} got notif_init_expert notification about meeting {meeting_id}')


async def feedback_notif_applicant(meeting_id):
    md = db.get_meeting(meeting_id)
    await dp.bot.send_message(md[3], text="✋🏻 Привет! Вчера у тебя была встреча с специалистом Росатома. "
                                          "Мы будем тебе признательны, если ты оставишь обратную связь. "
                                          "Это поможет нам проводить консультации на более высоком уровне!",
                              reply_markup=kb2b("Оставить отзыв", f"applicant_fb_agree_{md[0]}",
                                                "Не хочу писать отзыв", "applicant_menu"))
    logger.debug(f'Applicant {md[3]} got feedback_notif_applicant notification about meeting {meeting_id}')


async def feedback_notif_expert(meeting_id):
    md = db.get_meeting(meeting_id)
    await dp.bot.send_message(md[2], text="✋🏻 Привет! Вчера у вас была встреча с соискателем. "
                                          "Мы будем признательны, если вы оставите обратную связь. "
                                          "Это поможет нам проводить консультации на более высоком уровне!",
                              reply_markup=kb2b("Оставить отзыв", f"expert_fb_agree_{md[0]}",
                                                "Не хочу писать отзыв", "expert_menu"))
    logger.debug(f'Expert {md[2]} got feedback_notif_applicant notification about meeting {meeting_id}')


async def notif_after_show_contacts(pressed_user_id, second_user_id):
    await dp.bot.send_message(pressed_user_id,
                              text="Удалось ли связаться с собеседником?",
                              reply_markup=kb2b("Да", f"local_contact_yes_{second_user_id}",
                                                "Нет", f"local_contact_no_{second_user_id}"))
    logger.debug(f'User {pressed_user_id} got notif_after_show_contacts notification about'
                 f' local contact with {second_user_id}')


@dp.callback_query_handler(Regexp(r'^local_contact_'))
async def local_contact_took_place_or_not(call: CallbackQuery):
    second_user_id = call.data.split("_")[3]

    choice = call.data.split("_")[2]
    if choice == "yes":
        status = "Связались"
    else:
        status = "Не связались"

    db.add_local_contact(call.from_user.id, second_user_id, status)

    await call.message.edit_reply_markup()
    await call.message.edit_text("Спасибо за ответ!")

    logger.debug(f'User {call.from_user.id} entered local_contact_took_place_or_not handler')
