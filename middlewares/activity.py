from datetime import datetime
from typing import (
    Dict,
    Union,
)

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from context import USER_TABLE
from database import (
    Applicant,
    Expert,
)
from loader import PostgresSession


__all__ = (
    'TrackUserActivityMiddleware',
)


class TrackUserActivityMiddleware(BaseMiddleware):
    async def on_process_callback_query(self, call: types.CallbackQuery, callback_data: Dict):
        if table := USER_TABLE.get():
            with PostgresSession.begin() as session:
                user: Union[Applicant, Expert] = session.query(table).get(call.from_user.id)  # type: ignore
                user.last_activity_time = datetime.utcnow().timestamp()  # .replace(tzinfo=pytz.utc).astimezone(tz)
                user.last_pressed_button = call.message.reply_markup[callback_data['row']][callback_data['column']].text
