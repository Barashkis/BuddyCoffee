import re

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards import directions_kb, division_kb, topics_kb, expert_menu_kb
from loader import dp, db, bot
from my_logger import logger


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
    db.update_user('experts', 'direction', call.from_user.id, call.data)
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
        db.update_user('experts', 'division', call.from_user.id, call.data)
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
    await message.answer(text="Какое время для встреч вам удобно? "
                              "Пожалуйста, напишите не менее 5 слотов для записи. <b>Укажите московское время</b>\n\n"
                              "<i>Формат:\n"
                              "25.01.2022 17:00, 27.01.2022 12:30, "
                              "28.01.2022 10:00, 31.01.2022 10:45, 02.02.2022 16:15</i>",
                              disable_notification=True)
    await state.set_state('expert_6')
    logger.debug(f"Expert {message.from_user.id} entered expert_5 handler")


@dp.message_handler(state='expert_6')
async def expert_6(message: Message, state: FSMContext):
    text = message.text
    flg = 0
    try:
        slots_list = text.split(',')
        slots_list = [slot.rstrip().lstrip() for slot in slots_list]
        for slot in slots_list:
            if re.match("^\d{1,2}\.\d{1,2}\.\d{4} \d{1,2}:\d{1,2}$", slot) is None:
                await message.answer(text=f'Бот не смог распознать следующий слот: <i>{slot}</i>\n\n'
                                          f'Пожалуйста, придерживайтесь формата. Отправьте временные слоты еще раз',
                                     disable_notification=True)
                await state.set_state('expert_6')
                flg = 1
                logger.debug(f"Expert {message.from_user.id} entered expert_6 handler but write incorrect slot: {slot}")
                break
        if flg == 0:
            db.update_user('experts', 'slots', message.from_user.id, message.text)
            await message.answer(text="С удовольствием поговорю на следующие темы:",
                                 reply_markup=topics_kb(),
                                 disable_notification=True)
            await state.set_state('expert_6.1')
            logger.debug(f"Expert {message.from_user.id} entered expert_6 handler")
    except Exception as e:
        logger.warning(f"Expert {message.from_user.id} entered expert_6 handler but got an error: {e}")
        await message.answer(text=f'Бот не смог распознать ваш ответ\n\n'
                                  f'Пожалуйста, придерживайтесь формата. Отправьте временные слоты еще раз',
                             disable_notification=True)
        await state.set_state('expert_6')


@dp.callback_query_handler(state='expert_6.1')
async def expert_6_1(call: CallbackQuery, state: FSMContext):
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
        await state.set_state('expert_6.1')
    else:
        sdata = await state.get_data()
        if sdata.get('list') is None or not sdata['list']:  # if user did not choose any button
            await call.message.answer('Пожалуйста, выберите минимум одну тему.')
            await state.set_state('expert_6.1')
        else:
            db.update_user('experts', 'topics', call.from_user.id, str(sdata['list'])[1:-1])
            username = db.get_expert(call.from_user.id)[2]
            if not username:
                await call.message.edit_reply_markup()
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
                await call.message.answer(text="Поздравляем, вы заполнили анкету. "
                                               "Можно приступать к поиску собеседника",
                                          reply_markup=expert_menu_kb,
                                          disable_notification=True)
                await call.message.edit_reply_markup()
                await state.finish()
    logger.debug(f"Expert {call.from_user.id} entered expert_6_1 handler with cd {call.data} and sd {sdata}")

@dp.message_handler(state='expert_7')
async def expert_6(message: Message, state: FSMContext):
    text = message.text
    if text[0] == '@':
        db.update_user('experts', 'wr_username', message.from_user.id, message.text[1:].rstrip())
        await message.answer(text="Поздравляем, вы заполнили анкету. "
                                       "Можно приступать к поиску собеседника",
                             reply_markup=expert_menu_kb,
                             disable_notification=True)
        await state.finish()
    else:
        await message.answer(text="Пожалуйста, напишите свой username корректно, начиная с '@'",
                             disable_notification=True)
        await state.set_state('expert_7')
    logger.debug(f"Expert {message.from_user.id} entered expert_6 handler with message: {text}")