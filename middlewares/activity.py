from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from sqlalchemy import func

from database import Statistic
from loader import PostgresSession


__all__ = (
    'TrackUserActivityMiddleware',
)


class TrackUserActivityMiddleware(BaseMiddleware):
    async def on_process_callback_query(self, call: types.CallbackQuery, _):
        callback_data = call.data.split(':')
        row, column = int(callback_data[-2]), int(callback_data[-1])
        with PostgresSession.begin() as session:
            user_stat: Statistic = session.query(Statistic).get(call.from_user.id)
            if user_stat:
                user_stat.presses += 1
                user_stat.last_activity_time = func.now()
                user_stat.last_pressed_button = (
                    call.message.reply_markup.inline_keyboard[row][column].text
                )
