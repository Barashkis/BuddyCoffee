from typing import (
    Literal,
    Tuple,
)

from aiogram.utils.callback_data import CallbackData


__all__ = (
    'BaseCallbackData',
    'choosing_time_cd',
)


def _perform_callback_data_keys(*args: str) -> Tuple[str, Literal['row'], Literal['column']]:
    return *args, 'row', 'column'


class BaseCallbackData:
    callback_data = CallbackData(
        'base_cd',
        *_perform_callback_data_keys('value')
    )

    def __init__(self, value, row, column):
        self.value = value
        self.row = row
        self.column = column

    def construct(self):
        return self.callback_data.new(
            value=self.value,
            row=self.row,
            column=self.column,
        )


choosing_time_cd = CallbackData(
    'choosing_time_a',
    *_perform_callback_data_keys('expert_id', 'slot', 'init_by', 'action', 'meeting_id')
)
