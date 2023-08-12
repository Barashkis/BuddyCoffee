from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from config import directions_list, topics_list
from handlers.utils import track_user_activity
from keyboards import directions_kb, applicant_menu_kb, topics_kb, kb2b
from loader import dp, db
from my_logger import logger


@dp.callback_query_handler(text='applicant_start')
async def applicant_start(call: CallbackQuery, state: FSMContext):
    user = call.from_user

    if db.get_expert(user.id) is not None:
        track_user_activity(user.id, "applicants", "Сменить роль")

        db.remove_user("experts", user.id)

        logger.debug(f"Expert {user.id} was removed from database")

    logger.debug(f"Applicant {user.id} entered applicant_start handler")
    date = call.message.date.strftime('%d.%m.%Y %H:%M')
    try:
        db.add_applicant(user.id, date, user.username, user.first_name, user.last_name)
        await call.answer(cache_time=5)
        await call.message.answer(text="Давай знакомиться! Напиши свое имя.\n\n"
                                       "<i>Формат: Иван</i>",
                                  disable_notification=True)
        await call.message.edit_reply_markup()
        await state.set_state('applicant_1')
    except Exception as e:
        logger.debug(f"Applicant {user.id} was not recorded as a new user: {e}")


@dp.message_handler(state='applicant_1')
async def applicant_1(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'wr_firstname', user_id, message.text)
    await message.answer(text="Напиши свою фамилию.\n\n"
                              "<i>Формат: Иванов</i>",
                         disable_notification=True)
    await state.set_state('applicant_2')
    logger.debug(f"Applicant {user_id} entered applicant_1 handler")


@dp.message_handler(state='applicant_2')
async def applicant_2(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'wr_lastname', user_id, message.text)
    await message.answer(text="Выбери свое направление:",
                         reply_markup=directions_kb,
                         disable_notification=True)
    await state.set_state('applicant_3')
    logger.debug(f"Applicant {user_id} entered applicant_2 handler")


@dp.callback_query_handler(state='applicant_3')
async def applicant_3(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    db.update_user('applicants', 'direction', user_id, directions_list[int(call.data)])
    await call.answer(cache_time=5)
    await call.message.answer(text="Расскажи кратко о своем опыте и местах работы (при наличии).\n\n"
                                   "<i>Пример: Изучал программирование на C# и С++, обладаю знаниями в Python, имею "
                                   "опыт удалённой работы, проходил стажировку в IT-интеграторе "
                                   "ГК «Росатом» — Гринатоме</i>",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('applicant_4')
    logger.debug(f"Applicant {user_id} entered applicant_3 handler")


@dp.message_handler(state='applicant_4')
async def applicant_4(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'profile', user_id, message.text)
    await message.answer(text="Укажи наименование учебного заведения, которое "
                              "ты окончил (или в котором учишься), специальность и уровень образования.\n\n"
                              "<i>Формат: МФТИ, «Компьютерные науки и инженерия», полное высшее образование</i>",
                         disable_notification=True)
    await state.set_state('applicant_5')
    logger.debug(f"Applicant {user_id} entered applicant_4 handler")


@dp.message_handler(state='applicant_5')
async def applicant_5(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'institution', user_id, message.text)
    await message.answer(text="Напиши год окончания университета (или планируемый).\n\n"
                              "<i>Формат: 2022</i>",
                         disable_notification=True)
    await state.set_state('applicant_6')
    logger.debug(f"Applicant {user_id} entered applicant_5 handler")


@dp.message_handler(state='applicant_6')
async def applicant_6(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'grad_year', user_id, message.text)
    await message.answer(text="Напиши город/регион, который тебе наиболее интересен для трудоустройства.\n\n"
                              "<i>Формат: Москва</i>",
                         disable_notification=True)
    await state.set_state('applicant_7')
    logger.debug(f"Applicant {user_id} entered applicant_6 handler")


@dp.message_handler(state='applicant_7')
async def applicant_7(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'empl_region', user_id, message.text)
    await message.answer(text="Поделись своими интересами и хобби.\n\n"
                              "<i>Пример: В свободное время смотрю курсы по разработке игр, увлекаюсь музыкой и "
                              "компьютерными играми, люблю играть в футбол и выезжать на природу</i>",
                         disable_notification=True)
    await state.set_state('applicant_8')
    logger.debug(f"Applicant {user_id} entered applicant_7 handler")


@dp.message_handler(state='applicant_8')
async def applicant_8(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'hobby', user_id, message.text)
    await message.answer(text="Выбери основные темы, которые ты хочешь обсудить:",
                         reply_markup=topics_kb(),
                         disable_notification=True)
    await state.set_state('applicant_8.1')
    logger.debug(f"Applicant {user_id} entered applicant_8 handler")


@dp.callback_query_handler(state='applicant_8.1')
async def applicant_8_1(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    cdata = call.data
    if cdata != 'done':
        async with state.proxy() as data:
            if 'list' in data:
                if int(cdata) in data['list']:
                    data['list'].remove(int(cdata))
                else:
                    data['list'].append(int(cdata))
            else:
                data['list'] = [int(cdata)]
        sdata = await state.get_data()
        await call.message.edit_reply_markup(topics_kb(sdata['list']))
        await state.set_state('applicant_8.1')
    else:
        sdata = await state.get_data()
        if sdata.get('list') is None or not sdata['list']:  # if user did not choose any button
            await call.answer()
            await call.message.answer('Пожалуйста, выбери минимум одну тему')
            await state.set_state('applicant_8.1')
        else:
            db.update_user('applicants', 'topics', user_id, str(sdata['list'])[1:-1])
            await call.message.answer(text="О чем хочешь узнать и какие вопросы обсудить на онлайн-встрече?\n\n"
                                           "<i>Пример: Хочу узнать подробнее о трудоустройстве в цифровые компании ГК "
                                           "«Росатом» на позицию разработчика C#: стек технологий, должностные "
                                           "обязанности, применяются ли технологии разработки Agile, Waterfall</i>",
                                      disable_notification=True)
            await call.message.edit_reply_markup()
            await state.set_state('applicant_9')
    logger.debug(f"Applicant {user_id} entered applicant_8_1 handler with cd {call.data} and sd {sdata}")


@dp.message_handler(state='applicant_9')
async def applicant_9(message: Message, state: FSMContext):
    user_id = message.from_user.id

    db.update_user('applicants', 'topics_details', user_id, message.text)
    await message.answer("Нажми \"Да\", чтобы мы могли показывать твои контактные данные в телеграм "
                         f"(@{message.from_user.username}) экспертам. Так они смогут связаться с тобой, если "
                         "проблема с конференцией. Если ты не хочешь, "
                         "чтобы тебе писали эксперты, нажми \"Нет\"",
                         reply_markup=kb2b("Да", "yes", "Нет", "no"))
    await state.set_state('applicant_10')
    logger.debug(f"Applicant {user_id} entered applicant_9 handler")


@dp.callback_query_handler(state='applicant_10')
async def applicant_10(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if "yes" == call.data:
        agree_to_show_contacts = True
    else:
        agree_to_show_contacts = False
    db.update_user('applicants', 'agree_to_show_contacts', user_id, agree_to_show_contacts)

    u_data = db.get_applicant(user_id)
    firstname = u_data[5]
    lastname = u_data[6]
    direction = u_data[7]
    profile = u_data[8]
    institution = u_data[9]
    grad_year = u_data[10]
    empl_region = u_data[11]
    hobby = u_data[12]
    topics = ', '.join([topics_list.get(int(i)) for i in u_data[13].split(', ')])
    topics_details = u_data[14]

    await call.message.edit_reply_markup()
    await call.message.answer(text=f"Поздравляем, ты заполнил анкету. "
                                   f"Теперь, ты можешь приступить к поиску специалистов.\n\n"
                                   f"Твоя анкета:\n"
                                   f"<b>Имя:</b> {firstname}\n"
                                   f"<b>Фамилия:</b> {lastname}\n"
                                   f"<b>Направление:</b> {direction}\n"
                                   f"<b>Опыт:</b> {profile}\n"
                                   f"<b>Учебное заведение:</b> {institution}\n"
                                   f"<b>Год окончания:</b> {grad_year}\n"
                                   f"<b>Регион трудоустройства:</b> {empl_region}\n"
                                   f"<b>Хобби:</b> {hobby}\n"
                                   f"<b>Темы на обсуждение:</b> {topics}\n"
                                   f"<b>Вопросы ко встрече:</b> {topics_details}\n\n",
                              reply_markup=applicant_menu_kb,
                              disable_notification=True)
    await state.finish()
    logger.debug(f"Applicant {user_id} entered applicant_11 handler")
