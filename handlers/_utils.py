from typing import Any

from aiogram.dispatcher import FSMContext


async def update_state_registration_data(state: FSMContext, key: str, value: Any) -> None:
    await state.reset_state(with_data=False)
    async with state.proxy() as data:
        data['registration_data'][key] = value
