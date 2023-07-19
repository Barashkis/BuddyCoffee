from typing import Dict

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from sqlalchemy import delete

from database import (
    Applicant,
    Expert,
)
from loader import PostgresSession
from logger import logger


__all__ = (
    'DeleteFromDatabaseMiddleware',
)


class DeleteFromDatabaseMiddleware(BaseMiddleware):
    async def on_process_callback_query(self, call: types.CallbackQuery, data: Dict):
        state = data['state']
        state_name = await state.get_state()

        await state.set_state('role')
        async with state.proxy() as state_data:
            role = state_data.get('role')
        await state.set_state(state_name)

        if role:
            callback_value = call.data.split(':')[0]
            if callback_value in ['applicant_start', 'expert_start']:
                user_id = call.from_user.id
                with PostgresSession.begin() as session:
                    user = Applicant if role == 'a' else Expert
                    stmt = delete(user).where(user.id == user_id)
                    session.execute(stmt)

                logger.debug(f'Expert {user.id} was removed from database')
