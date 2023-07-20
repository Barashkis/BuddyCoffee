from typing import Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)

from config import (
    applicant_menu,
    directions,
    topics,
)
from database import (
    Applicant,
    Topic,
)
from keyboards import (
    base_cd,
    form_kb,
    kb_from_mapping,
)
from loader import (
    PostgresSession,
    dp,
)
from logger import logger

from ._utils import update_state_registration_data


@dp.callback_query_handler(base_cd.filter(value='applicant_start'))
async def applicant_start(call: CallbackQuery, state: FSMContext):
    user = call.from_user

    await call.message.edit_text(
        'Давай знакомиться! Напиши свое имя\n\n'
        '<i>Формат: Иван</i>'
    )
    async with state.proxy() as data:
        data['registration_data'] = {
            'id': user.id,
            'username': user.username,
            'tg_firstname': user.first_name,
            'tg_lastname': user.last_name,
        }
    await state.set_state('applicant_1')

    logger.debug(f'Applicant {user.id} enter applicant_start handler')


@dp.message_handler(state='applicant_1')
async def applicant_1(message: Message, state: FSMContext):
    await message.answer(
        'Напиши свою фамилию\n\n'
        '<i>Формат: Иванов</i>'
    )

    await update_state_registration_data(state, 'wr_firstname', message.text)
    await state.set_state('applicant_2')

    logger.debug(f'Applicant {message.from_user.id} enter applicant_1 handler')


@dp.message_handler(state='applicant_2')
async def applicant_2(message: Message, state: FSMContext):
    await message.answer('Выбери свое направление:', reply_markup=kb_from_mapping(directions))

    await update_state_registration_data(state, 'wr_lastname', message.text)
    await state.set_state('applicant_3')

    logger.debug(f'Applicant {message.from_user.id} enter applicant_2 handler')


@dp.callback_query_handler(base_cd.filter(), state='applicant_3')
async def applicant_3(call: CallbackQuery, callback_data: Dict, state: FSMContext):
    await call.message.edit_text(
        'Расскажи кратко о своем опыте и местах работы (при наличии)\n\n'
        '<i>Пример: Изучал программирование на C# и С++, обладаю знаниями в Python, имею '
        'опыт удалённой работы, проходил стажировку в IT-интеграторе ГК «Росатом» — Гринатоме</i>'
    )

    await update_state_registration_data(state, 'direction', directions[int(callback_data['value'])])
    await state.set_state('applicant_4')

    logger.debug(f'Applicant {call.from_user.id} enter applicant_3 handler')


@dp.message_handler(state='applicant_4')
async def applicant_4(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.debug(f'Applicant {user_id} enter applicant_4 handler')

    await message.answer(
        'Укажи наименование учебного заведения, которое '
        'ты окончил (или в котором учишься), специальность и уровень образования\n\n'
        '<i>Формат: МФТИ, «Компьютерные науки и инженерия», полное высшее образование</i>'
    )

    await update_state_registration_data(state, 'profile', message.text)
    await state.set_state('applicant_5')


@dp.message_handler(state='applicant_5')
async def applicant_5(message: Message, state: FSMContext):
    await message.answer(
        'Напиши год окончания университета (или планируемый)\n\n'
        '<i>Формат: 2022</i>'
    )

    await update_state_registration_data(state, 'institution', message.text)
    await state.set_state('applicant_6')

    logger.debug(f'Applicant {message.from_user.id} enter applicant_5 handler')


@dp.message_handler(state='applicant_6')
async def applicant_6(message: Message, state: FSMContext):
    await message.answer(
        'Напиши город/регион, который тебе наиболее интересен для трудоустройства\n\n'
        '<i>Формат: Москва</i>'
    )

    await update_state_registration_data(state, 'graduation_year', message.text)
    await state.set_state('applicant_7')

    logger.debug(f'Applicant {message.from_user.id} enter applicant_6 handler')


@dp.message_handler(state='applicant_7')
async def applicant_7(message: Message, state: FSMContext):
    await message.answer(
        'Поделись своими интересами и хобби\n\n'
        '<i>Пример: В свободное время смотрю курсы по разработке игр, увлекаюсь музыкой и '
        'компьютерными играми, люблю играть в футбол и выезжать на природу</i>'
    )

    await update_state_registration_data(state, 'employment_region', message.text)
    await state.set_state('applicant_8')

    logger.debug(f'Applicant {message.from_user.id} entered applicant_7 handler')


@dp.message_handler(state='applicant_8')
async def applicant_8(message: Message, state: FSMContext):
    await message.answer(
        'Выбери основные темы, которые ты хочешь обсудить:',
        reply_markup=form_kb(topics),
    )

    await update_state_registration_data(state, 'hobby', message.text)
    await state.set_state('applicant_8.1')

    logger.debug(f'Applicant {message.from_user.id} enter applicant_8 handler')


@dp.callback_query_handler(base_cd.filter(), state='applicant_8.1')
async def applicant_8_1(call: CallbackQuery, callback_data: Dict, state: FSMContext):
    button_type = 'selected'
    async with state.proxy() as state_data:
        if (callback_value := callback_data['value']) != 'send_form':
            callback_value = int(callback_value)
            if (k := 'pressed_buttons') in state_data:
                if callback_value in state_data[k]:
                    button_type = 'unselected'
                    state_data[k].remove(callback_value)
                else:
                    state_data[k].append(callback_value)
            else:
                state_data[k] = [callback_value]

            await call.message.edit_reply_markup(form_kb(topics, state_data[k]))
        else:
            if not (chosen_buttons := state_data.get('pressed_buttons')):
                await call.answer()
                await call.message.answer('Пожалуйста, выбери минимум одну тему')
            else:
                await call.message.edit_text(
                    'О чем хочешь узнать и какие вопросы обсудить на онлайн-встрече?\n\n'
                    '<i>Пример: Хочу узнать подробнее о трудоустройстве в цифровые компании ГК '
                    '«Росатом» на позицию разработчика C#: стек технологий, должностные '
                    'обязанности, применяются ли технологии разработки Agile, Waterfall</i>',
                )

                await update_state_registration_data(state, 'topics', chosen_buttons)
                await state.set_state('applicant_9')

        logger.debug(
            f'Applicant {call.from_user.id} enter applicant_8_1 handler. '
            f'Callback\'s {button_type} button value - {callback_value!r}'
        )


@dp.message_handler(state='applicant_9')
async def applicant_9(message: Message, state: FSMContext):
    await update_state_registration_data(state, 'topics_details', message.text)
    with PostgresSession.begin() as session:
        async with state.proxy() as state_data:
            registration_data = state_data['registration_data']
            topics_ids = registration_data.pop('topics')
            await message.answer(
                'Поздравляем, ты заполнил анкету. Теперь, ты можешь приступить к поиску специалистов\n\n'
                'Твоя анкета:\n'
                f'<b>Имя:</b> {registration_data["wr_firstname"]}\n'
                f'<b>Фамилия:</b> {registration_data["wr_lastname"]}\n'
                f'<b>Направление:</b> {registration_data["direction"]}\n'
                f'<b>Опыт:</b> {registration_data["profile"]}\n'
                f'<b>Учебное заведение:</b> {registration_data["institution"]}\n'
                f'<b>Год окончания:</b> {registration_data["graduation_year"]}\n'
                f'<b>Регион трудоустройства:</b> {registration_data["employment_region"]}\n'
                f'<b>Хобби:</b> {registration_data["hobby"]}\n'
                f'<b>Темы на обсуждение:</b> {", ".join([topics[i] for i in topics_ids])}\n'
                f'<b>Вопросы ко встрече:</b> {registration_data["topics_details"]}\n\n',
                reply_markup=kb_from_mapping(applicant_menu),
            )

            applicant = Applicant(**registration_data)
            applicant.topics = [t for t in session.query(Topic).all() if t.id in topics_ids]
            session.add(applicant)
        await state.reset_data()

    logger.debug(f'Applicant {message.from_user.id} entered applicant_9 handler')
