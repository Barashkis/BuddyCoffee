from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import (
    BigInteger,
    String,
    Text,
)


class PostgresBase(DeclarativeBase):
    pass


applicant_topic_association_table = Table(
    'applicant_topic_association_table',
    PostgresBase.metadata,
    Column('applicant_id', ForeignKey('applicant.id')),
    Column('topic_id', ForeignKey('topic.id')),
)

expert_topic_association_table = Table(
    'expert_topic_association_table',
    PostgresBase.metadata,
    Column('expert_id', ForeignKey('expert.id')),
    Column('topic_id', ForeignKey('topic.id')),
)


class Applicant(PostgresBase):
    __tablename__ = 'applicant'

    id = mapped_column(BigInteger(), primary_key=True)
    join_date: Mapped[datetime]
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    firstname: Mapped[str] = mapped_column(String(100))
    lastname: Mapped[str] = mapped_column(String(100))
    wr_firstname: Mapped[str] = mapped_column(String(100))
    wr_lastname: Mapped[str] = mapped_column(String(100))
    profile = mapped_column(Text())
    institution = mapped_column(Text())
    grad_year: Mapped[int]
    empl_region = mapped_column(Text())
    hobby = mapped_column(Text())
    photo: Mapped[str]
    last_activity_time: Mapped[datetime]
    presses: Mapped[int] = mapped_column(default=0)
    direction_id = mapped_column(ForeignKey('direction.id'))
    status_id = mapped_column(ForeignKey('user_status.id'))
    topics: Mapped[List['Topic']] = relationship(
        secondary=applicant_topic_association_table,
        back_populates='applicants'
    )

    status: Mapped['UserStatus'] = relationship(back_populates='applicants')
    direction: Mapped['Direction'] = relationship(back_populates='applicants')

    meetings: Mapped[List['Meeting']] = relationship(back_populates='applicant')
    local_contacts: Mapped[List['LocalContact']] = relationship(back_populates='applicant')


class Expert(PostgresBase):
    __tablename__ = 'expert'

    id = mapped_column(BigInteger(), primary_key=True)
    join_date: Mapped[datetime]
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    firstname: Mapped[str] = mapped_column(String(100))
    lastname: Mapped[str] = mapped_column(String(100))
    wr_fullname: Mapped[str] = mapped_column(String(100))
    profile = mapped_column(Text())
    photo: Mapped[str]
    last_activity_time: Mapped[datetime]
    presses: Mapped[int] = mapped_column(default=0)
    status_id = mapped_column(ForeignKey('user_status.id'))
    direction_id = mapped_column(ForeignKey('direction.id'))
    division_id = mapped_column(ForeignKey('division.id'))
    topics: Mapped[List['Topic']] = relationship(secondary=expert_topic_association_table, back_populates='experts')

    status: Mapped['UserStatus'] = relationship(back_populates='experts')
    direction: Mapped['Direction'] = relationship(back_populates='experts')
    division: Mapped['Division'] = relationship(back_populates='experts')

    meetings: Mapped[List['Meeting']] = relationship(back_populates='expert')
    local_contacts: Mapped[List['LocalContact']] = relationship(back_populates='expert')


class Topic(PostgresBase):
    __tablename__ = 'topic'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    applicants: Mapped[List['Applicant']] = relationship(
        secondary=applicant_topic_association_table,
        back_populates='topics'
    )
    experts: Mapped[List['Expert']] = relationship(secondary=expert_topic_association_table, back_populates='topics')


class Meeting(PostgresBase):
    __tablename__ = 'meeting'

    api_id = mapped_column(BigInteger(), primary_key=True)
    date: Mapped[datetime]
    link: Mapped[str]
    expert_fb = mapped_column(Text())
    applicant_fb = mapped_column(Text())
    expert_confirmed: Mapped[bool]
    applicant_confirmed: Mapped[bool]
    applicant_id = mapped_column(ForeignKey('applicant.id'))
    expert_id = mapped_column(ForeignKey('expert.id'))
    status_id = mapped_column(ForeignKey('meeting_status.id'))

    applicant: Mapped['Applicant'] = relationship(back_populates='meetings')
    expert: Mapped['Expert'] = relationship(back_populates='meetings')
    status: Mapped['MeetingStatus'] = relationship(back_populates='meetings')

    notifications: Mapped[List['Notification']] = relationship(back_populates='meeting')


class LocalContact(PostgresBase):
    __tablename__ = 'local_contact'

    id: Mapped[int] = mapped_column(primary_key=True)
    expert_id = mapped_column(ForeignKey('expert.id'))
    applicant_id = mapped_column(ForeignKey('applicant.id'))
    status_id = mapped_column(ForeignKey('local_contact_status.id'))

    applicant: Mapped['Applicant'] = relationship(back_populates='local_contacts')
    expert: Mapped['Expert'] = relationship(back_populates='local_contacts')
    status: Mapped['LocalContactStatus'] = relationship(back_populates='local_contacts')


class Direction(PostgresBase):
    __tablename__ = 'direction'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    applicants: Mapped[List['Applicant']] = relationship(back_populates='direction')
    experts: Mapped[List['Expert']] = relationship(back_populates='direction')


class Division(PostgresBase):
    __tablename__ = 'division'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    experts: Mapped[List['Expert']] = relationship(back_populates='division')


class Notification(PostgresBase):
    __tablename__ = 'notification'

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    meeting_id = mapped_column(ForeignKey('meeting.api_id'))

    meeting: Mapped['Meeting'] = relationship(back_populates='notifications')


class UserStatus(PostgresBase):
    __tablename__ = 'user_status'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    applicants: Mapped[List['Applicant']] = relationship(back_populates='status')
    experts: Mapped[List['Expert']] = relationship(back_populates='status')


class MeetingStatus(PostgresBase):
    __tablename__ = 'meeting_status'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    meetings: Mapped[List['Meeting']] = relationship(back_populates='status')


class LocalContactStatus(PostgresBase):
    __tablename__ = 'local_contact_status'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    local_contacts: Mapped[List['LocalContact']] = relationship(back_populates='status')


class Migration(PostgresBase):
    __tablename__ = '_migration'

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(default=0)
