from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)

from database.postgres import (
    Applicant,
    Direction,
    Division,
    Expert,
    LocalContact,
    LocalContactStatus,
    Meeting,
    MeetingStatus,
    Migration,
    Notification,
    PostgresBase,
    Topic,
    UserStatus,
)


__all__ = (
    "PostgresBase",
    "Applicant",
    "Expert",
    "Topic",
    "Meeting",
    "LocalContact",
    "Direction",
    "Division",
    "Notification",
    "MeetingStatus",
    "UserStatus",
    "LocalContactStatus",
    "Migration",
    "new_engine"
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
