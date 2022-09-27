from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from config import directions_list, topics_list, divisions_list
from keyboards import directions_kb, division_kb, topics_kb, kb3b, kb2b, expert_profile_bk
from loader import dp, db
from my_logger import logger


@dp.callback_query_handler(text='change_prof_e')
async def check_profile_e(call: CallbackQuery):
    u_data = db.get_expert(call.from_user.id)
    fullname= u_data[5]
    direction = directions_list.get(int(u_data[6]))
    if u_data[7] is None:
        division = u_data[8]
    else:
        division = divisions_list.get(int(u_data[7]))
    profile = u_data[10]
    topics = ', '.join([topics_list.get(int(i)) for i in u_data[12].split(', ')])
    await call.message.answer(text=f"Сейчас ваш профиль выглядит так\n\n"
                              f"<b>Имя:</b> {fullname}\n"
                              f"<b>Направление:</b> {direction}\n"
                              f"<b>Дивизион:</b> {division}\n"                                 
                              f"<b>Опыт:</b> {profile}\n"
                              f"<b>Темы на обсуждение:</b> {topics}",
                              reply_markup=kb3b("Хочу изменить", "change_prof_e2", "Все ок", "expert_menu", "Сменить роль", "warn_change_role_e"),
                              disable_notification=True)
    logger.debug(f'Expert {call.from_user.id} entered check_profile_e handler')


@dp.callback_query_handler(text='warn_change_role_e')
async def warn_change_role_e(call: CallbackQuery):
    await call.message.answer(
        """Вы точно хотите сменить роль?
Студент — учащийся или выпускник, который хочет узнать больше о карьере в Росатоме и получить консультацию от эксперта
Эксперты — сотрудники Росатома, которые консультируют соискателей
""",
        reply_markup=kb2b("Да, я уверен", "applicant_start", "Назад", "change_prof_e"),
        disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f'Expert {call.from_user.id} entered warn_change_role_e handler')


@dp.callback_query_handler(text='change_prof_e2')
async def change_profile_e(call: CallbackQuery):
    await call.message.answer(text="Какое поле вы хотите изменить?",
                              reply_markup=expert_profile_bk,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logger.debug(f'Expert {call.from_user.id} entered change_profile_e handler')


# Fullname
@dp.callback_query_handler(text='che_fullname')
async def che_fullname(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Напишите свое имя",
                              disable_notification=True)
    await state.set_state('che_fullname')
    await call.message.edit_reply_markup()
    logger.debug(f'Expert {call.from_user.id} entered che_fullname handler')


@dp.message_handler(state='che_fullname')
async def che_fullname2(message: Message, state: FSMContext):
    db.update_user('experts', 'wr_fullname', message.from_user.id, message.text)
    await message.answer(text=f"Ваше имя изменено на <i>{message.text}</i>",
                         reply_markup=expert_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Expert {message.from_user.id} entered che_fullname2 handler')


# Direction
@dp.callback_query_handler(text='che_direction')
async def che_direction(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Выберите нужное направление",
                              reply_markup=directions_kb,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('che_direction')
    logger.debug(f'Expert {call.from_user.id} entered che_direction handler')


@dp.callback_query_handler(state='che_direction')
async def che_direction2(call: CallbackQuery, state: FSMContext):
    db.update_user('experts', 'direction', call.from_user.id, call.data)
    await call.message.answer(text=f"Ваше направление было обновлено",
                              reply_markup=expert_profile_bk,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.finish()
    logger.debug(f'Expert {call.from_user.id} entered che_direction2 handler')


# Division
@dp.callback_query_handler(text='che_division')
async def che_division(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Выберите нужный дивизион",
                              reply_markup=division_kb,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('che_division')
    logger.debug(f'Expert {call.from_user.id} entered che_division handler')


@dp.callback_query_handler(state='che_division')
async def che_division2(call: CallbackQuery, state: FSMContext):
    if call.data == 'other':
        await call.message.answer("Напишите название вашего дивизиона:")
        await call.message.edit_reply_markup()
        await state.set_state('che_division2_1')
    else:
        db.update_user('experts', 'division', call.from_user.id, call.data)
        db.update_user('experts', 'wr_division', call.from_user.id, None)
        await call.message.answer(text="Ваш дивизион был изменен",
                                  reply_markup=expert_profile_bk,
                                  disable_notification=True)
        await call.message.edit_reply_markup()
        await state.finish()
    logger.debug(f'Expert {call.from_user.id} entered che_division2 handler with cd {call.data}')


@dp.message_handler(state='che_division2_1')
async def che_division2_1(message: Message, state: FSMContext):
    db.update_user('experts', 'wr_division', message.from_user.id, message.text)
    db.update_user('experts', 'division', message.from_user.id, None)
    await message.answer(text="Ваш дивизион был изменен",
                         reply_markup=expert_profile_bk,
                         disable_notification=True)
    await state.finish()
    logger.debug(f'Expert {message.from_user.id} entered che_division2_1 handler')


# Position
@dp.callback_query_handler(text='che_position')
async def che_position(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Укажите вашу должность\n\n"
                              "<i>Формат: Frontend Developer</i>",
                              disable_notification=True)
    await state.set_state('che_position')
    await call.message.edit_reply_markup()
    logger.debug(f'Expert {call.from_user.id} entered che_position handler')


@dp.message_handler(state='che_position')
async def che_position2(message: Message, state: FSMContext):
    db.update_user('experts', 'position', message.from_user.id, message.text)
    await message.answer(text=f"Ваша должность изменена на <i>{message.text}</i>",
                         reply_markup=expert_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Expert {message.from_user.id} entered che_position2 handler')


# Profile
@dp.callback_query_handler(text='che_profile')
async def che_profile(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Расскажите о своей экспертизе\n\n"
                              "<i>Пример: Разрабатываю frontend-часть enterprise веб-приложений и пользовательские "
                              "элементы управления. Свободно владею HTML5, CSS3 (LESS/SASS), DOM, "
                              "JavaScript/TypeScript. Имею опыт работы с Angular/React /Vue.js, работаю с Git, "
                              "BootsTrap. Знаю принципы и технологии веб-сайтов, асинхронных веб-приложений, MVC, "
                              "Razor, http-интерфейсы, умею работать с графическими редакторами, читаю код на "
                              "C# и Java</i>",
                              disable_notification=True)
    await state.set_state('che_profile')
    await call.message.edit_reply_markup()
    logger.debug(f'Expert {call.from_user.id} entered che_profile handler')


@dp.message_handler(state='che_profile')
async def che_profile2(message: Message, state: FSMContext):
    db.update_user('experts', 'profile', message.from_user.id, message.text)
    await message.answer(text=f"Ваша экспертиза была изменена",
                         reply_markup=expert_profile_bk,
                              disable_notification=True)
    await state.finish()
    logger.debug(f'Expert {message.from_user.id} entered che_profile2 handler')


# Topics
@dp.callback_query_handler(text='che_topics')
async def che_topics(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Выберите основные темы, которые вы хотите обсудить:",
                              reply_markup=topics_kb(),
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('che_topics')
    logger.debug(f'Expert {call.from_user.id} entered che_topics handler')


@dp.callback_query_handler(state='che_topics')
async def che_topics2(call: CallbackQuery, state: FSMContext):
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
        await state.set_state('che_topics')
    else:
        sdata = await state.get_data()
        if sdata.get('list') is None or not sdata['list']:  # if user did not choose any button
            await call.message.answer('Пожалуйста, выберите минимум одну тему.')
            await state.set_state('che_topics')
        else:
            db.update_user('experts', 'topics', call.from_user.id, str(sdata['list'])[1:-1])
            await call.message.answer(text="Темы для обсуждения были изменены",
                                      reply_markup=expert_profile_bk,
                                      disable_notification=True)
            await call.message.edit_reply_markup()
            await state.finish()
    logger.debug(f'Expert {call.from_user.id} entered che_topics2 handler with cd {call.data}')
