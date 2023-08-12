import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from config import directions_list, divisions_list, topics_list

choosing_time_cd = CallbackData('choosing_time_a', 'expert_id', 'slot', 'init_by', 'action', 'meeting_id')


def kb1b(txt, cd):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt, callback_data=cd)
            ]
        ]
    )
    return kb


def kb2b(txt1, cd1, txt2, cd2):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=txt1, callback_data=cd1)],
            [InlineKeyboardButton(text=txt2, callback_data=cd2)]
        ]
    )
    return kb


def kb3b(txt1, cd1, txt2, cd2, txt3, cd3):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=txt1, callback_data=cd1)],
            [InlineKeyboardButton(text=txt2, callback_data=cd2)],
            [InlineKeyboardButton(text=txt3, callback_data=cd3)]
        ]
    )
    return kb


def kb4b(txt1, cd1, txt2, cd2, txt3, cd3, txt4, cd4):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=txt1, callback_data=cd1)],
            [InlineKeyboardButton(text=txt2, callback_data=cd2)],
            [InlineKeyboardButton(text=txt3, callback_data=cd3)],
            [InlineKeyboardButton(text=txt4, callback_data=cd4)]
        ]
    )
    return kb


directions_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=directions_list.get(1), callback_data='1')],
        [InlineKeyboardButton(text=directions_list.get(2), callback_data='2')],
        [InlineKeyboardButton(text=directions_list.get(3), callback_data='3')],
        [InlineKeyboardButton(text=directions_list.get(4), callback_data='4')],
        [InlineKeyboardButton(text=directions_list.get(5), callback_data='5')],
        [InlineKeyboardButton(text=directions_list.get(6), callback_data='6')],
        [InlineKeyboardButton(text=directions_list.get(7), callback_data='7')],
        [InlineKeyboardButton(text=directions_list.get(8), callback_data='8')],
        [InlineKeyboardButton(text=directions_list.get(9), callback_data='9')],
        [InlineKeyboardButton(text=directions_list.get(10), callback_data='10')]
    ]
)

division_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=divisions_list.get(1), callback_data='1')],
        [InlineKeyboardButton(text=divisions_list.get(2), callback_data='2')],
        [InlineKeyboardButton(text=divisions_list.get(3), callback_data='3')],
        [InlineKeyboardButton(text=divisions_list.get(4), callback_data='4')],
        [InlineKeyboardButton(text=divisions_list.get(5), callback_data='5')],
        [InlineKeyboardButton(text=divisions_list.get(6), callback_data='6')],
        [InlineKeyboardButton(text=divisions_list.get(7), callback_data='7')],
        [InlineKeyboardButton(text=divisions_list.get(8), callback_data='8')],
        [InlineKeyboardButton(text=divisions_list.get(9), callback_data='9')],
        [InlineKeyboardButton(text=divisions_list.get(10), callback_data='10')],
        [InlineKeyboardButton(text=divisions_list.get(11), callback_data='11')],
        [InlineKeyboardButton(text=divisions_list.get(12), callback_data='12')],
        [InlineKeyboardButton(text=divisions_list.get(13), callback_data='13')],
        [InlineKeyboardButton(text=divisions_list.get(14), callback_data='14')],
        [InlineKeyboardButton(text='Другой', callback_data='other')]
    ]
)

expert_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Посмотреть анкеты соискателей', callback_data='search_applicants')],
        [InlineKeyboardButton(text='Мои встречи', callback_data='expert_meetings')],
        [InlineKeyboardButton(text='Добавить фото к анкете', callback_data='add_photo_e')],
        [InlineKeyboardButton(text='Изменить профиль', callback_data='change_prof_e')],
        [InlineKeyboardButton(text='Согласие на сообщение контактных данных соискателям', callback_data='change_agreement_to_show_contacts_e')]
    ]
)

applicant_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Начать поиск специалистов', callback_data='search_experts')],
        [InlineKeyboardButton(text='Мои встречи', callback_data='applicant_meetings')],
        [InlineKeyboardButton(text='Добавить фото к анкете', callback_data='add_photo_a')],
        [InlineKeyboardButton(text='Изменить профиль', callback_data='change_prof_a')],
        [InlineKeyboardButton(text='FAQ', callback_data='faq_a')],
        [InlineKeyboardButton(text='Согласие на сообщение контактных данных экспертам', callback_data='change_agreement_to_show_contacts_a')]
    ]
)


def topics_kb(chosen_buttons: list = None):
    b1 = InlineKeyboardButton(text=topics_list.get(1), callback_data='1')
    b2 = InlineKeyboardButton(text=topics_list.get(2), callback_data='2')
    b3 = InlineKeyboardButton(text=topics_list.get(3), callback_data='3')
    b4 = InlineKeyboardButton(text=topics_list.get(4), callback_data='4')
    b5 = InlineKeyboardButton(text=topics_list.get(5), callback_data='5')
    b6 = InlineKeyboardButton(text=topics_list.get(6), callback_data='6')
    b7 = InlineKeyboardButton(text=topics_list.get(7), callback_data='7')
    b8 = InlineKeyboardButton(text=topics_list.get(8), callback_data='8')
    b9 = InlineKeyboardButton(text=topics_list.get(9), callback_data='9')
    buttons_list = [b1, b2, b3, b4, b5, b6, b7, b8, b9]
    done = InlineKeyboardButton(text='Готово 👌', callback_data='done')
    topics_keyboard = InlineKeyboardMarkup(row_width=1)
    if chosen_buttons is None:
        chosen_buttons = []
    for i, b in enumerate(buttons_list):
        if i + 1 in chosen_buttons:
            b.text += ' ✅'
        topics_keyboard.add(b)
    topics_keyboard.add(done)
    return topics_keyboard


applicant_profile_bk = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Имя', callback_data='cha_firstname')],
        [InlineKeyboardButton(text='Фамилия', callback_data='cha_lastname')],
        [InlineKeyboardButton(text='Направление', callback_data='cha_direction')],
        [InlineKeyboardButton(text='Опыт', callback_data='cha_profile')],
        [InlineKeyboardButton(text='Учебное заведение', callback_data='cha_institution')],
        [InlineKeyboardButton(text='Год окончания', callback_data='cha_grad_year')],
        [InlineKeyboardButton(text='Регион трудоустройства', callback_data='cha_empl_region')],
        [InlineKeyboardButton(text='Хобби', callback_data='cha_hobby')],
        [InlineKeyboardButton(text='Темы на обсуждение', callback_data='cha_topics')],
        [InlineKeyboardButton(text='Вопросы ко встрече', callback_data='cha_topics_details')],
        [InlineKeyboardButton(text='Назад', callback_data='change_prof_a')]
    ]
)


expert_profile_bk = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Имя', callback_data='che_fullname')],
        [InlineKeyboardButton(text='Направление', callback_data='che_direction')],
        [InlineKeyboardButton(text='Дивизион', callback_data='che_division')],
        [InlineKeyboardButton(text='Опыт', callback_data='che_profile')],
        [InlineKeyboardButton(text='Темы на обсуждение', callback_data='che_topics')],
        [InlineKeyboardButton(text='Назад', callback_data='change_prof_e')]
    ]
)


def suitable_experts_kb2(suitable_experts: list, page: int = 1):
    experts_keyboard = InlineKeyboardMarkup()
    n_experts = len(suitable_experts)
    if page > 1:
        prev_b = InlineKeyboardButton(text='⏮', callback_data=f'sekbp_{page - 1}')
        choose_b = InlineKeyboardButton(text='Выбрать',
                                        callback_data=f"choosee_{suitable_experts[page - 1].get('user_id')}")
        if n_experts > page:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'sekbp_{page + 1}')
        else:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
    else:
        prev_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        choose_b = InlineKeyboardButton(text='Выбрать',
                                        callback_data=f"choosee_{suitable_experts[page - 1].get('user_id')}")
        if n_experts > page:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'sekbp_{page + 1}')
        else:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
    experts_keyboard.row(prev_b, choose_b, next_b)
    experts_keyboard.add(InlineKeyboardButton(text='Назад', callback_data='applicant_menu'))
    return experts_keyboard


def suitable_applicants_kb2(suitable_applicants: list, page: int = 1):
    applicants_keyboard = InlineKeyboardMarkup()
    n_applicants = len(suitable_applicants)
    if page > 1:
        prev_b = InlineKeyboardButton(text='⏮', callback_data=f'sakbp_{page - 1}')
        choose_b = InlineKeyboardButton(text='Выбрать',
                                        callback_data=f"choosea_{suitable_applicants[page - 1].get('user_id')}")
        if n_applicants > page:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'sakbp_{page + 1}')
        else:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
    else:
        prev_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        choose_b = InlineKeyboardButton(text='Выбрать',
                                        callback_data=f"choosea_{suitable_applicants[page - 1].get('user_id')}")
        if n_applicants > page:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'sakbp_{page + 1}')
        else:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
    applicants_keyboard.row(prev_b, choose_b, next_b)
    applicants_keyboard.add(InlineKeyboardButton(text='Назад', callback_data='expert_menu'))
    return applicants_keyboard


def experts_to_confirm_kb2(experts_to_confirm: list, page: int = 1):
    experts_keyboard = InlineKeyboardMarkup()
    n_experts = len(experts_to_confirm)
    if page > 1:
        prev_b = InlineKeyboardButton(text='⏮', callback_data=f'admin_sekbp_{page - 1}')
        choose_b = InlineKeyboardButton(text='Выбрать',
                                        callback_data=f"admin_choosee_{experts_to_confirm[page - 1][0]}")
        if n_experts > page:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'admin_sekbp_{page + 1}')
        else:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
    else:
        prev_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        choose_b = InlineKeyboardButton(text='Выбрать',
                                        callback_data=f"admin_choosee_{experts_to_confirm[page - 1][0]}")
        if n_experts > page:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'admin_sekbp_{page + 1}')
        else:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
    experts_keyboard.row(prev_b, choose_b, next_b)
    experts_keyboard.add(InlineKeyboardButton(text='Назад', callback_data='close_keyboard'))
    return experts_keyboard


def slots_kb(expert_id: int, init_by: str, slots: list, action: str, meeting_id: int, page: int = 1):
    slots_keyboard = InlineKeyboardMarkup()
    spl = 9  # slots per list
    l = len(slots)
    n_pages = math.ceil(l / spl)  # number of pages

    if n_pages > 1:
        end_index = spl * page if page < n_pages else l

        for i in range(spl * (page - 1), end_index):
            slot_for_cd = slots[i].replace(":", "%")

            try:
                slots_keyboard.add(InlineKeyboardButton(text=slots[i],
                                                        callback_data=choosing_time_cd.new(expert_id=expert_id,
                                                                                           slot=slot_for_cd,
                                                                                           init_by=init_by,
                                                                                           action=action,
                                                                                           meeting_id=meeting_id)))
            except IndexError:
                pass
        if page == 1:
            prev_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        else:
            prev_b = InlineKeyboardButton(text='⏮', callback_data=f'skbp_{expert_id}_{page - 1}_init_by_{init_by}_{action}_{meeting_id}')
        if page == n_pages:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        else:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'skbp_{expert_id}_{page + 1}_init_by_{init_by}_{action}_{meeting_id}')
        slots_keyboard.row(prev_b, next_b)
    else:
        for i in range(0, l):
            slot_for_cd = slots[i].replace(":", "%")
            slots_keyboard.add(InlineKeyboardButton(text=slots[i],
                                                    callback_data=choosing_time_cd.new(expert_id=expert_id,
                                                                                       slot=slot_for_cd,
                                                                                       init_by=init_by,
                                                                                       action=action,
                                                                                       meeting_id=meeting_id)))
    return slots_keyboard


def meetings_a_kb(meetings: list, page: int = 1):
    meetings_keyboard = InlineKeyboardMarkup()
    mpl = 9  # meetings per list
    l = len(meetings)
    n_pages = math.ceil(l / mpl)  # number of pages

    if n_pages > 1:
        for i in range(mpl * (page - 1), mpl * page):
            try:
                meetings_keyboard.add(InlineKeyboardButton(text=meetings[i][4],
                                                           callback_data=f'meeting_a_{meetings[i][0]}'))
            except IndexError:
                pass
        if page == 1:
            prev_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        else:
            prev_b = InlineKeyboardButton(text='⏮', callback_data=f'mkbp_a_{page - 1}')
        if page == n_pages:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        else:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'mkbp_a_{page + 1}')
        meetings_keyboard.row(prev_b, next_b)
        meetings_keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'applicant_menu'))
    else:
        for i in range(0, l):
            meetings_keyboard.add(InlineKeyboardButton(text=meetings[i][4],
                                                       callback_data=f'meeting_a_{meetings[i][0]}'))
        meetings_keyboard.add(InlineKeyboardButton(text='Назад', callback_data='applicant_menu'))
    return meetings_keyboard


def meetings_e_kb(meetings: list, page: int = 1):
    meetings_keyboard = InlineKeyboardMarkup()
    mpl = 9  # meetings per list
    l = len(meetings)
    n_pages = math.ceil(l / mpl)  # number of pages

    if n_pages > 1:
        for i in range(mpl * (page - 1), mpl * page):
            try:
                meetings_keyboard.add(InlineKeyboardButton(text=meetings[i][4],
                                                           callback_data=f'meeting_e_{meetings[i][0]}'))
            except IndexError:
                pass
        if page == 1:
            prev_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        else:
            prev_b = InlineKeyboardButton(text='⏮', callback_data=f'mkbp_e_{page - 1}')
        if page == n_pages:
            next_b = InlineKeyboardButton(text=' ', callback_data=f'no_callback')
        else:
            next_b = InlineKeyboardButton(text='⏭', callback_data=f'mkbp_e_{page + 1}')
        meetings_keyboard.row(prev_b, next_b)
        meetings_keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'expert_menu'))
    else:
        for i in range(0, l):
            meetings_keyboard.add(InlineKeyboardButton(text=meetings[i][4],
                                                       callback_data=f'meeting_e_{meetings[i][0]}'))
        meetings_keyboard.add(InlineKeyboardButton(text='Назад', callback_data='expert_menu'))
    return meetings_keyboard
