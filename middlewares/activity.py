from datetime import datetime
from typing import Dict

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from config import tz
from context import USER_TABLE
from loader import PostgresSession


__all__ = (
    'TrackUserActivityMiddleware',
)


class TrackUserActivityMiddleware(BaseMiddleware):
    async def on_process_callback_query(self, call: types.CallbackQuery, callback_data: Dict):
        if table := USER_TABLE.get():
            with PostgresSession.begin() as session:
                user = session.query(table).get(call.from_user.id)
                user.last_activity = (
                    f"{datetime.now().astimezone(tz).strftime('%d.%m.%Y %H:%M:%S')}, "
                    f"кнопка {call.message.reply_markup[callback_data['row']][callback_data['column']].text}"
                )
