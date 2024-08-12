from datetime import datetime

from aiogram.dispatcher.filters import Regexp
from aiogram.types import CallbackQuery
from pytz import timezone

from keyboards import kb2b
from loader import dp, db, tz
from my_logger import logger


async def notif_cancel_to_expert2(expert_id):
    await dp.bot.send_message(expert_id, text=f'К сожалению, соискатель отказался от встречи. По кнопке '
                                              f'"Посмотреть анкеты соискателей" можно выбрать другого соискателя')
    logger.debug(f'Expert {expert_id} got notif_cancel_to_expert2 notification')


async def notif_cancel_to_expert3(expert_id):
    await dp.bot.send_message(expert_id, text=f'К сожалению, соискатель отказался переносить встречу')
    logger.debug(f'Expert {expert_id} got notif_cancel_to_expert3 notification')


async def notif_cancel_to_applicant(applicant_id, meeting_date, expert_name):
    await dp.bot.send_message(applicant_id, text=f'{expert_name} отменил встречу, назначенную на {meeting_date}')
    logger.debug(f'Applicant {applicant_id} got notif_cancel_to_applicant notification of {meeting_date} meeting')


async def notif_cancel_to_applicant2(applicant_id):
    await dp.bot.send_message(applicant_id, text=f'К сожалению, текущий график выбранного эксперта перегружен. '
                                                 f'Давай попробуем выбрать другого эксперта?')
    logger.debug(f'Applicant {applicant_id} got notif_cancel_to_applicant2 notification')


async def notif_cancel_to_applicant3(applicant_id):
    await dp.bot.send_message(applicant_id, text='К сожалению, текущий график выбранного '
                                                 'эксперта не позволяет перенести эту встречу')
    logger.debug(f'Applicant {applicant_id} got notif_cancel_to_applicant3 notification')


async def notif_init_applicant(applicant_id, slot, expert_fullname, meeting_id):
    await dp.bot.send_message(
        applicant_id,
        text=f'Специалист {expert_fullname} назначил вам встречу на '
             f'{datetime.fromtimestamp(slot).astimezone(timezone(tz)).strftime("%d.%m.%Y %H:%M")}. '
             '<b>Указано московское время</b>. Вы подтверждаете ее?',
        reply_markup=kb2b(
            "Подтверждаю ✅", f'approved_a_c_{meeting_id}',
            "Не подтверждаю ❌", f"denied_a_c_{meeting_id}",
        )
    )
    logger.debug(f'Applicant {applicant_id} got notif_init_applicant notification')


async def notif_reschedule_applicant(applicant_id, slot, expert_fullname, meeting_id):
    await dp.bot.send_message(
        applicant_id,
        text=f'Специалист {expert_fullname} предлагает перенести встречу на '
             f'{datetime.fromtimestamp(slot).astimezone(timezone(tz)).strftime("%d.%m.%Y %H:%M")}. '
             '<b>Указано московское время</b>. Вы подтверждаете перенос?',
        reply_markup=kb2b(
            "Подтверждаю ✅", f'approved_a_r_{meeting_id}_{slot}',
            "Не подтверждаю ❌", f"denied_a_r_{meeting_id}"
        )
    )
    logger.debug(f'Applicant {applicant_id} got notif_reschedule_applicant notification')


async def notif_cancel_3hours_to_expert(expert_id):
    await dp.bot.send_message(expert_id, text=f'К сожалению, соискатель отказался от встречи. По кнопке "Посмотреть '
                                              f'анкеты соискателей" можно выбрать другого соискателя')
    logger.debug(f'Expert {expert_id} got notif_cancel_3hours_to_expert notification')


async def notif_1day(applicant_id):
    await dp.bot.send_message(applicant_id,
                              text="Напоминаем о запланированной встрече. Подробности о встрече ты можешь "
                                   "узнать в меню 'Мои встречи'")
    logger.debug(f'Applicant {applicant_id} got notif_1day notification')


async def notif_3hours(applicant_id, meeting_id):
    await dp.bot.send_message(applicant_id, text="Твоя консультация состоится через 3 часа!")
    logger.debug(f'Applicant {applicant_id} got notif_3hours notification about {meeting_id} meeting')


async def notif_1hour(applicant_id):
    await dp.bot.send_message(applicant_id, text="Твоя консультация состоится уже через час!")
    logger.debug(f'Applicant {applicant_id} got notif_1hour notification')


async def notif_5min(applicant_id):
    await dp.bot.send_message(applicant_id, text="До начала консультации осталось 5 минут!")
    logger.debug(f'Applicant {applicant_id} got notif_5min notification')


async def notif_cancel_to_expert(expert_id, meeting_date, applicant_name):
    await dp.bot.send_message(expert_id, text=f'{applicant_name} отменил встречу, назначенную на {meeting_date}')
    logger.debug(f'Expert {expert_id} got notif_cancel_to_expert notification about {meeting_date} meeting')


async def notif_init_expert(expert_id, slot, applicant_name, meeting_id):
    await dp.bot.send_message(expert_id, text=f'Соискатель {applicant_name} назначил вам встречу на {slot}. <b>Указано московское время</b>. '
                                              f'Вы подтверждаете ее?',
                              reply_markup=kb2b("Подтверждаю ✅", f'approved_e_c_{meeting_id}',
                                                "Не подтверждаю ❌", f"denied_e_c_{meeting_id}"))
    logger.debug(f'Expert {expert_id} got notif_init_expert notification about meeting {meeting_id}')


async def notif_reschedule_expert(expert_id, slot, applicant_name, meeting_id):
    await dp.bot.send_message(expert_id, text=f'Соискатель {applicant_name} предлагает перенести встречу на {slot}. <b>Указано московское время</b>. '
                                              f'Вы подтверждаете ее?',
                              reply_markup=kb2b("Подтверждаю ✅", f'approved_e_r_{meeting_id}_{slot}',
                                                "Не подтверждаю ❌", f'denied_e_r_{meeting_id}'))
    logger.debug(f'Expert {expert_id} got notif_reschedule_expert notification about meeting {meeting_id}')


async def feedback_notif_applicant(meeting_id):
    md = db.get_meeting(meeting_id)
    await dp.bot.send_message(md[3], text="✋🏻 Привет! Час назад у тебя была встреча с специалистом Росатома. "
                                          "Мы будем тебе признательны, если ты оценишь эксперта, с которым ты общался, "
                                          "по шкале от 1 до 5, где 1 — встреча не принесла желаемых результатов, "
                                          "эксперт не смог ответить на интересующие вопросы, "
                                          "5 — всё прошло замечательно, эксперт ответил на все вопросы, "
                                          "помог разобраться. В следующем сообщении мы попросим оставить тебя обратную "
                                          "связь. Напиши там, как прошла встреча и почему ты поставил такую оценку"
                                          "эксперту. Это поможет нам стать ещё лучше!",
                              reply_markup=kb2b("Оставить отзыв", f"applicant_fb_agree_{md[0]}",
                                                "Не хочу писать отзыв", "applicant_menu"))
    logger.debug(f'Applicant {md[3]} got feedback_notif_applicant notification about meeting {meeting_id}')


async def feedback_notif_expert(meeting_id):
    md = db.get_meeting(meeting_id)
    await dp.bot.send_message(md[2], text="✋🏻 Привет! Час назад у вас была встреча с соискателем. "
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
