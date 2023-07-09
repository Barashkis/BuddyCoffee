from aiogram import Dispatcher

from .activity import TrackUserActivityMiddleware


def setup(dp: Dispatcher) -> None:
    dp.middleware.setup(TrackUserActivityMiddleware())
