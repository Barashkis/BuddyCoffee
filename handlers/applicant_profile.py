from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from config import topics_list, directions_list
from keyboards import directions_kb, topics_kb, kb3b, kb2b, applicant_profile_bk
from loader import dp, db
from my_logger import logger


@dp.callback_query_handler(text='change_prof_a')
async def check_profile_a(call: CallbackQuery):
    u_data = db.get_applicant(call.from_user.id)
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
    await call.message.answer(text=f"Сейчас твоя анкета выглядит так\n\n"
                              f"<b>Имя:</b> {firstname}\n"
                              f"<b>Фамилия:</b> {lastname}\n"
                              f"<b>Направление:</b> {direction}\n"
                              f"<b>Опыт:</b> {profile}\n"
                              f"<b>Учебное заведение:</b> {institution}\n"
                              f"<b>Год окончания:</b> {grad_year}\n"
                              f"<b>Регион трудоустройства:</b> {empl_region}\n"
                              f"<b>Хобби:</b> {hobby}\n"
                              f"<b>Темы на обсуждение:</b> {topics}\n"
                              f"<b>Вопросы ко встрече:</b> {topics_details}",
                              reply_markup=kb3b("Хочу изменить", "change_prof_a2", "Все ок", "applicant_menu", "Сменить роль", "warn_change_role_a"),
                              disable_notification=True)
    logger.debug(f'Applicant {call.from_user.id} entered check_profile_a handler')


@dp.callback_query_handler(text='warn_change_role_a')
async def warn_change_role_a(call: CallbackQuery):
    await call.message.answer(
        """Ты точно хочешь сменить роль?
Студент — учащийся или выпускник, который хочет узнать больше о карьере в Росатоме и получить консультацию от эксперта
Эксперты — сотрудники Росатома, которые консультируют соискателей
""",
        reply_markup=kb2b("Да, я уверен", "expert_start", "Назад", "change_prof_a"),
        disable_notification=True
    )
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered warn_change_role_a handler')


@dp.callback_query_handler(text='change_prof_a2')
async def change_profile_a(call: CallbackQuery):
    await call.message.answer(text="Какое поле ты хочешь изменить?",
                              reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered change_profile_a handler')


# Firstname
@dp.callback_query_handler(text='cha_firstname')
async def cha_firstname(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Напиши свое имя",
                              disable_notification=True)
    await state.set_state('cha_firstname')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_firstname handler')


@dp.message_handler(state='cha_firstname')
async def cha_firstname2(message: Message, state: FSMContext):
    db.update_user('applicants', 'wr_firstname', message.from_user.id, message.text)
    await message.answer(text=f"Твое имя изменено на <i>{message.text}</i>",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_firstname2 handler')


# Lastname
@dp.callback_query_handler(text='cha_lastname')
async def cha_lastname(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Напиши свою фамилию",
                              disable_notification=True)
    await state.set_state('cha_lastname')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_lastname handler')


@dp.message_handler(state='cha_lastname')
async def cha_lastname2(message: Message, state: FSMContext):
    db.update_user('applicants', 'wr_lastname', message.from_user.id, message.text)
    await message.answer(text=f"Твоя фамилия изменена на <i>{message.text}</i>",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_lastname2 handler')


# Direction
@dp.callback_query_handler(text='cha_direction')
async def cha_direction(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Выбери нужное направление",
                              reply_markup=directions_kb,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('cha_direction')
    logger.debug(f'Applicant {call.from_user.id} entered cha_direction handler')


@dp.callback_query_handler(state='cha_direction')
async def cha_direction2(call: CallbackQuery, state: FSMContext):
    db.update_user('applicants', 'direction', call.from_user.id, directions_list[int(call.data)])
    await call.message.answer(text=f"Твое направление было обновлено",
                              reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.finish()
    logger.debug(f'Applicant {call.from_user.id} entered cha_direction2 handler')


# Profile
@dp.callback_query_handler(text='cha_profile')
async def cha_profile(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Расскажи кратко о своем опыте и местах работы (при наличии).\n\n"
                                   "<i>Пример: Изучал программирование на C# и С++, обладаю знаниями в Python, имею "
                                   "опыт удалённой работы, проходил стажировку в IT-интеграторе "
                                   "ГК «Росатом» — Гринатоме</i>",
                              disable_notification=True)
    await state.set_state('cha_profile')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_profile handler')


@dp.message_handler(state='cha_profile')
async def cha_profile2(message: Message, state: FSMContext):
    db.update_user('applicants', 'profile', message.from_user.id, message.text)
    await message.answer(text=f"Твой опыт был изменен",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_profile2 handler')


# Institution
@dp.callback_query_handler(text='cha_institution')
async def cha_institution(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Укажи наименование учебного заведения, которое "
                              "ты окончил (или в котором учишься), специальность и уровень образования.\n\n"
                              "<i>Формат: МФТИ, «Компьютерные науки и инженерия», полное высшее образование</i>",
                              disable_notification=True)
    await state.set_state('cha_institution')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_institution handler')


@dp.message_handler(state='cha_institution')
async def cha_institution2(message: Message, state: FSMContext):
    db.update_user('applicants', 'institution', message.from_user.id, message.text)
    await message.answer(text=f"Твой учебное заведение было изменено",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_institution2 handler')


# Graduation year
@dp.callback_query_handler(text='cha_grad_year')
async def cha_grad_year(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Напиши год окончания университета (или планируемый).\n\n"
                              "<i>Формат: 2022</i>",
                              disable_notification=True)
    await state.set_state('cha_grad_year')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_grad_year handler')


@dp.message_handler(state='cha_grad_year')
async def cha_grad_year2(message: Message, state: FSMContext):
    db.update_user('applicants', 'grad_year', message.from_user.id, message.text)
    await message.answer(text=f"Твой год окончания учебного заведения был изменен",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_grad_year2 handler')


# Employment region
@dp.callback_query_handler(text='cha_empl_region')
async def cha_empl_region(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Напиши город/регион, который тебе наиболее интересен для трудоустройства.\n\n"
                              "<i>Формат: Москва</i>",
                              disable_notification=True)
    await state.set_state('cha_empl_region')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_empl_region handler')


@dp.message_handler(state='cha_empl_region')
async def cha_empl_region2(message: Message, state: FSMContext):
    db.update_user('applicants', 'empl_region', message.from_user.id, message.text)
    await message.answer(text=f"Твой желаемый регион для трудоустройства был изменен",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_empl_region2 handler')


# Hobby
@dp.callback_query_handler(text='cha_hobby')
async def cha_hobby(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Поделись своими интересами и хобби.\n\n"
                              "<i>Пример: В свободное время смотрю курсы по разработке игр, увлекаюсь музыкой и "
                              "компьютерными играми, люблю играть в футбол и выезжать на природу</i>",
                              disable_notification=True)
    await state.set_state('cha_hobby')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_hobby handler')


@dp.message_handler(state='cha_hobby')
async def cha_hobby2(message: Message, state: FSMContext):
    db.update_user('applicants', 'hobby', message.from_user.id, message.text)
    await message.answer(text=f"Твои хобби были изменены",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_hobby2 handler')


# Topics
@dp.callback_query_handler(text='cha_topics')
async def cha_topics(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Выбери основные темы, которые ты хочешь обсудить:",
                              reply_markup=topics_kb(),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('cha_topics')
    logger.debug(f'Applicant {call.from_user.id} entered cha_topics handler')


@dp.callback_query_handler(state='cha_topics')
async def cha_topics2(call: CallbackQuery, state: FSMContext):
    cdata = call.data
    if cdata != 'done':  # if user dont press "Done" button
        async with state.proxy() as data:
            if 'list' in data:  # if it is not first click on button and list is not exist
                if int(cdata) in data['list']:  # if button is already chosen
                    data['list'].remove(int(cdata))
                else:
                    data['list'].append(int(cdata))
            else:
                data['list'] = [int(cdata)]
        sdata = await state.get_data()
        await call.message.edit_reply_markup(topics_kb(sdata['list']))
        await state.set_state('cha_topics')
    else:
        sdata = await state.get_data()
        if sdata.get('list') is None or not sdata['list']:  # if user did not choose any button
            await call.message.answer('Пожалуйста, выбери минимум одну тему.')
            await state.set_state('cha_topics')
        else:
            db.update_user('applicants', 'topics', call.from_user.id, str(sdata['list'])[1:-1])
            await call.message.answer(text="Темы для обсуждения были изменены",
                                      reply_markup=applicant_profile_bk,
                                      disable_notification=True)
            await call.message.edit_reply_markup()
            await state.finish()
    logger.debug(f'Applicant {call.from_user.id} entered cha_topics2 handler with cd {call.data}')


# Topics details
@dp.callback_query_handler(text='cha_topics_details')
async def cha_topics_details(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="О чем хочешь узнать и какие вопросы обсудить на онлайн-встрече?\n\n"
                                   "<i>Пример: Хочу узнать подробнее о трудоустройстве в цифровые компании ГК "
                                   "«Росатом» на позицию разработчика C#: стек технологий, должностные "
                                   "обязанности, применяются ли технологии разработки Agile, Waterfall</i>",
                              disable_notification=True)
    await state.set_state('cha_topics_details')
    await call.message.edit_reply_markup()
    logger.debug(f'Applicant {call.from_user.id} entered cha_topics_details handler')


@dp.message_handler(state='cha_topics_details')
async def cha_topics_details2(message: Message, state: FSMContext):
    db.update_user('applicants', 'topics_details', message.from_user.id, message.text)
    await message.answer(text=f"Вопросы для встречи были изменены",
                         reply_markup=applicant_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Applicant {message.from_user.id} entered cha_topics_details2 handler')
