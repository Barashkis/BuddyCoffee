import math
from datetime import datetime
from typing import (
    Dict,
    List,
    Literal,
)

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from callback_data import (
    BaseCallbackData,
    choosing_time_cd,
)

from config import (
    meetings_per_page,
    slots_per_page,
    tz,
    users_per_page,
)


def _buttons_from_dict(data: Dict) -> List[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=data[k],
        callback_data=BaseCallbackData(k, i, 0).construct()
    )
        for i, k in enumerate(data)]


def kb_from_dict(data: Dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for button in _buttons_from_dict(data):
        kb.add(button)

    return kb


def form_kb(data: Dict, chosen_buttons: List = None) -> InlineKeyboardMarkup:  # type: ignore
    kb = InlineKeyboardMarkup()
    chosen_buttons = chosen_buttons or []

    buttons_list = _buttons_from_dict(data)
    for i, button in enumerate(buttons_list, start=1):
        if i + 1 in chosen_buttons:
            button.text += ' ✅'
        kb.add(button)
    kb.add(
        InlineKeyboardButton(
            text='Готово 👌',
            callback_data=BaseCallbackData('send_form', -1, 0).construct()
        )
    )

    return kb


def suitable_users_kb(
        suitable_users: ...,
        user_type: Literal['a', 'e'],
        page: int = 1,
        to_confirm: bool = False
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    total_pages = math.ceil(len(suitable_users) / users_per_page)

    previous_button = (
        InlineKeyboardButton(
            text='⏮',
            callback_data=BaseCallbackData(f'request_{user_type}_{page - 1}', 0, 0).construct()
        ) if page > 1 else
        InlineKeyboardButton(
            text=' ',
            callback_data=BaseCallbackData('no_callback', 0, 0).construct()
        )
    )
    choose_button = InlineKeyboardButton(
        text='Выбрать',
        callback_data=BaseCallbackData(
            f'{"admin" if to_confirm else ""}_choose_{user_type}_{suitable_users[page - 1].get("user_id")}', 0, 1
        ).construct()
    )
    next_b = (
        InlineKeyboardButton(
            text='⏭',
            callback_data=BaseCallbackData(
                f'request_{user_type}_{page + 1}', 0, 2
            ).construct()
        ) if page < total_pages else
        InlineKeyboardButton(text=' ', callback_data=BaseCallbackData('no_callback', 0, 2).construct())
    )

    kb.row(previous_button, choose_button, next_b)
    kb.add(InlineKeyboardButton(text='Назад', callback_data=BaseCallbackData(f'menu_{user_type}', 1, 0).construct()))

    return kb


def slots_kb(
        expert_id: int,
        init_by: str,
        slots: ...,
        action: str,
        meeting_id: int,
        page: int = 1
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    slots_count = len(slots)
    total_pages = math.ceil(slots_count / slots_per_page)

    end_index = slots_per_page * page if page < total_pages else slots_count
    for i, v in enumerate(range(slots_per_page * (page - 1), end_index)):
        kb.add(
            InlineKeyboardButton(
                text=slots[v],
                callback_data=choosing_time_cd.new(
                    expert_id=expert_id,
                    slot=datetime.strptime(slots[v], '%d.%m.%Y %H:%M').astimezone(tz=tz).timestamp(),
                    init_by=init_by,
                    action=action,
                    meeting_id=meeting_id,
                    row=i,
                    column=0
                )
            )
        )

    if total_pages > 1:
        prev_b = (
            InlineKeyboardButton(
                text='⏮',
                callback_data=BaseCallbackData(
                    f'request_s_{expert_id}_{page - 1}_init_by_{init_by}_{action}_{meeting_id}', -1, 0
                ).construct()
            ) if page > 1 else
            InlineKeyboardButton(text=' ', callback_data=BaseCallbackData('no_callback', -1, 0).construct())
        )
        next_b = (
            InlineKeyboardButton(
                text='⏭',
                callback_data=BaseCallbackData(
                    f'request_s_{expert_id}_{page + 1}_init_by_{init_by}_{action}_{meeting_id}', -1, 1
                ).construct()
            ) if page < total_pages else
            InlineKeyboardButton(text=' ', callback_data=BaseCallbackData('no_callback', -1, 1).construct())
        )
        kb.row(prev_b, next_b)

    return kb


def meetings_kb(meetings: ..., user_type: Literal['a', 'e'], page: int = 1) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    meetings_count = len(meetings)
    total_pages = math.ceil(meetings_count / slots_per_page)

    end_index = slots_per_page * page if page < total_pages else meetings_count
    for i, v in enumerate(range(meetings_per_page * (page - 1), end_index)):
        kb.add(
            InlineKeyboardButton(
                text=meetings[v][4],
                callback_data=BaseCallbackData(f'meeting_{user_type}_{meetings[i][0]}', i, 0).construct()
            )
        )

    prev_b = (
        InlineKeyboardButton(
            text='⏮',
            callback_data=BaseCallbackData(f'request_m_{user_type}_{page - 1}', -2, 0).construct()
        ) if page > 1 else
        InlineKeyboardButton(
            text=' ',
            callback_data=BaseCallbackData('no_callback', -2, 0).construct()
        )
    )
    next_b = (
        InlineKeyboardButton(
            text='⏭',
            callback_data=BaseCallbackData(f'request_m_{user_type}_{page + 1}', -2, 1).construct()
        ) if page < total_pages else
        InlineKeyboardButton(
            text=' ',
            callback_data=BaseCallbackData('no_callback', -2, 1).construct()
        )
    )
    kb.row(prev_b, next_b)
    kb.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data=BaseCallbackData(f'menu_{user_type}', -1, 0).construct()
        )
    )

    return kb
