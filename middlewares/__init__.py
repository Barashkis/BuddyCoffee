from aiogram import Dispatcher

from .activity import TrackUserActivityMiddleware
from .change_role import DeleteFromDatabaseMiddleware


def setup(dp: Dispatcher) -> None:
    dp.middleware.setup(TrackUserActivityMiddleware())
    dp.middleware.setup(DeleteFromDatabaseMiddleware())
