from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards import directions_kb, division_kb, topics_kb
from loader import dp, db, bot
from my_logger import logger
from config import directions_list, divisions_list


@dp.callback_query_handler(text='expert_start')
async def expert_start(call: CallbackQuery, state: FSMContext):
    if db.get_applicant(call.from_user.id) is not None:
        db.remove_user("applicants", call.from_user.id)

        logger.debug(f"Applicant {call.from_user.id} was removed from database")

    logger.debug(f"Expert {call.from_user.id} entered expert_start handler")
    date = call.message.date.strftime('%d.%m.%Y %H:%M')
    try:
        db.add_expert(call.from_user.id, date, call.from_user.username, call.from_user.first_name,
                      call.from_user.last_name)
        await call.answer(cache_time=5)
        await call.message.answer(text="Как вас зовут?\n\n"
                                       "<i>Формат: Алексей</i>",
                                  disable_notification=True)
        await call.message.edit_reply_markup()
        await state.set_state('expert_1')
    except Exception as e:
        logger.debug(f"Expert {call.from_user.id} was not recorded as a new user: {e}")


@dp.message_handler(state='expert_1')
async def expert_1(message: Message, state: FSMContext):
    db.update_user('experts', 'wr_fullname', message.from_user.id, message.text)
    await message.answer(text="Выберите направление:",
                         reply_markup=directions_kb,
                         disable_notification=True)
    await state.set_state('expert_2')
    logger.debug(f"Expert {message.from_user.id} entered expert_1 handler")


@dp.callback_query_handler(state='expert_2')
async def expert_2(call: CallbackQuery, state: FSMContext):
    db.update_user('experts', 'direction', call.from_user.id, directions_list[int(call.data)])
    await call.answer(cache_time=5)
    await call.message.answer(text="Выберите дивизион:",
                              reply_markup=division_kb,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state('expert_3')
    logger.debug(f"Expert {call.from_user.id} entered expert_2 handler")


@dp.callback_query_handler(state='expert_3')
async def expert_2_1(call: CallbackQuery, state: FSMContext):
    if call.data == 'other':
        await call.message.answer("Напишите название вашего дивизиона:")
        await call.message.edit_reply_markup()
        await state.set_state('expert_3.1')
    else:
        db.update_user('experts', 'division', call.from_user.id, divisions_list[int(call.data)])
        await call.answer(cache_time=5)
        await call.message.answer(text="Расскажите о своей экспертизе\n\n"
                                  "<i>Пример: Разрабатываю frontend-часть enterprise веб-приложений и пользовательские "
                                  "элементы управления. Свободно владею HTML5, CSS3 (LESS/SASS), DOM, "
                                  "JavaScript/TypeScript. Имею опыт работы с Angular/React /Vue.js, работаю с Git, "
                                  "BootsTrap. Знаю принципы и технологии веб-сайтов, асинхронных веб-приложений, MVC, "
                                  "Razor, http-интерфейсы, умею работать с графическими редакторами, читаю код на "
                                  "C# и Java</i>",
                                  disable_notification=True)
        await call.message.edit_reply_markup()
        await state.set_state('expert_5')
    logger.debug(f"Expert {call.from_user.id} entered expert_2_1 handler with cd {call.data}")


@dp.message_handler(state='expert_3.1')
async def expert_3(message: Message, state: FSMContext):
    db.update_user('experts', 'wr_division', message.from_user.id, message.text)
    await message.answer(text="Расскажите о своей экспертизе\n\n"
                              "<i>Пример: Разрабатываю frontend-часть enterprise веб-приложений и пользовательские "
                              "элементы управления. Свободно владею HTML5, CSS3 (LESS/SASS), DOM, "
                              "JavaScript/TypeScript. Имею опыт работы с Angular/React /Vue.js, работаю с Git, "
                              "BootsTrap. Знаю принципы и технологии веб-сайтов, асинхронных веб-приложений, MVC, "
                              "Razor, http-интерфейсы, умею работать с графическими редакторами, читаю код на "
                              "C# и Java</i>",
                         disable_notification=True)
    await state.set_state('expert_5')
    logger.debug(f"Expert {message.from_user.id} entered expert_3 handler")


@dp.message_handler(state='expert_4')
async def expert_4(message: Message, state: FSMContext):
    db.update_user('experts', 'position', message.from_user.id, message.text)
    await message.answer(text="Расскажите о своей экспертизе\n\n"
                              "<i>Пример: Разрабатываю frontend-часть enterprise веб-приложений и пользовательские "
                              "элементы управления. Свободно владею HTML5, CSS3 (LESS/SASS), DOM, "
                              "JavaScript/TypeScript. Имею опыт работы с Angular/React /Vue.js, работаю с Git, "
                              "BootsTrap. Знаю принципы и технологии веб-сайтов, асинхронных веб-приложений, MVC, "
                              "Razor, http-интерфейсы, умею работать с графическими редакторами, читаю код на "
                              "C# и Java</i>",
                              disable_notification=True)
    await state.set_state('expert_5')
    logger.debug(f"Expert {message.from_user.id} entered expert_4 handler")


@dp.message_handler(state='expert_5')
async def expert_5(message: Message, state: FSMContext):
    db.update_user('experts', 'profile', message.from_user.id, message.text)
    await message.answer(text="С удовольствием поговорю на следующие темы:",
                         reply_markup=topics_kb(),
                         disable_notification=True)

    await state.set_state('expert_6')
    logger.debug(f"Expert {message.from_user.id} entered expert_5 handler")


@dp.callback_query_handler(state='expert_6')
async def expert_6(call: CallbackQuery, state: FSMContext):
    cdata = call.data
    if cdata != 'done':  # if user don't press "Done" button
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
        await state.set_state('expert_6')
    else:
        sdata = await state.get_data()
        if sdata.get('list') is None or not sdata['list']:  # if user did not choose any button
            await call.message.answer('Пожалуйста, выберите минимум одну тему.')
            await state.set_state('expert_6')
        else:
            await call.message.edit_reply_markup()

            db.update_user('experts', 'topics', call.from_user.id, str(sdata['list'])[1:-1])
            username = db.get_expert(call.from_user.id)[2]
            if not username:
                await call.message.answer(text="Напишите ваше имя пользователя (username) в Telegram. "
                                               "Если вы его не знаете, перейдите в «Настройки», затем нажмите "
                                               "на «Изменить профиль» (инструкция на изображениях ниже).\n\n"
                                               "Формат: @anthonytech")
                await bot.send_photo(chat_id=call.from_user.id,
                                     photo='https://i.ibb.co/7Gbg9c8/1.png',
                                     disable_notification=True)
                await bot.send_photo(chat_id=call.from_user.id,
                                     photo='https://i.ibb.co/m4Cmx9C/2.png',
                                     disable_notification=True)
                await bot.send_photo(chat_id=call.from_user.id,
                                     photo='https://i.ibb.co/hdBN7Bm/3.png',
                                     disable_notification=True)
                await bot.send_photo(chat_id=call.from_user.id,
                                     photo='https://i.ibb.co/f9yjs6Z/4.png',
                                     disable_notification=True)
                await state.set_state('expert_7')
            else:
                await call.message.answer("Поздравляем, вы заполнили анкету. "
                                          "Теперь дело за модераторами. Они рассмотрят Вашу анкету и "
                                          "в ближайшее время предоставят Вам фукнционал бота, если их все устроит")
                db.update_user('experts', 'status', call.from_user.id, "На модерации")
                await state.finish()
    logger.debug(f"Expert {call.from_user.id} entered expert_6 handler with cd {call.data} and sd {sdata}")


@dp.message_handler(state='expert_7')
async def expert_6(message: Message, state: FSMContext):
    text = message.text
    if text[0] == '@':
        db.update_user('experts', 'wr_username', message.from_user.id, message.text[1:].rstrip())
        await message.answer("Поздравляем, вы заполнили анкету. "
                             "Теперь дело за модераторами. Они рассмотрят Вашу анкету и "
                             "в ближайшее время предоставят Вам функционал бота или отправят анкету на доработку")
        db.update_user('experts', 'status', message.from_user.id, "На модерации")
        await state.finish()
    else:
        await message.answer(text="Пожалуйста, напишите свой username корректно, начиная с '@'",
                             disable_notification=True)
        await state.set_state('expert_7')
    logger.debug(f"Expert {message.from_user.id} entered expert_6 handler with message: {text}")
