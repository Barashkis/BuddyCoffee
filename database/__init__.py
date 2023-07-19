from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)

from .postgres import (
    Applicant,
    Expert,
    LocalContact,
    Meeting,
    Migration,
    Notification,
    PostgresBase,
    Statistic,
    Topic,
)


__all__ = (
    'PostgresBase',
    'Applicant',
    'Expert',
    'Topic',
    'Meeting',
    'LocalContact',
    'Notification',
    'Migration',
    'Statistic',
    'new_engine',
)


def new_engine(dialect, driver, user, password, host, name) -> Engine:
    url_object = URL.create(
        f'{dialect}+{driver}',
        username=user,
        password=password,
        host=host,
        database=name,
    )
    return create_engine(url_object)
