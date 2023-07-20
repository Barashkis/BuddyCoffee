from typing import List

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Table,
    func,
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

    id = mapped_column(BigInteger(), primary_key=True, index=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    username: Mapped[str] = mapped_column(String(50))
    tg_firstname: Mapped[str] = mapped_column(String(100))
    tg_lastname: Mapped[str] = mapped_column(String(100))
    wr_firstname = mapped_column(Text(), nullable=False)
    wr_lastname = mapped_column(Text(), nullable=False)
    profile = mapped_column(Text(), nullable=False)
    institution = mapped_column(Text(), nullable=False)
    graduation_year = mapped_column(Text(), nullable=False)
    employment_region = mapped_column(Text(), nullable=False)
    hobby = mapped_column(Text(), nullable=False)
    photo: Mapped[str] = mapped_column(Text(), nullable=True)
    topics_details = mapped_column(Text(), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str] = mapped_column(String(100), nullable=False)

    local_contacts: Mapped[List['LocalContact']] = relationship(back_populates='applicant')
    meetings: Mapped[List['Meeting']] = relationship(back_populates='applicant')

    topics: Mapped[List['Topic']] = relationship(
        secondary=applicant_topic_association_table,
        back_populates='applicants'
    )


class Expert(PostgresBase):
    __tablename__ = 'expert'

    id = mapped_column(BigInteger(), primary_key=True, index=True)
    date_created = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    username: Mapped[str] = mapped_column(String(50))
    tg_firstname: Mapped[str] = mapped_column(String(100))
    tg_lastname: Mapped[str] = mapped_column(String(100))
    wr_fullname: Mapped[str] = mapped_column(Text(), nullable=False)
    division: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str] = mapped_column(String(100), nullable=False)
    profile = mapped_column(Text(), nullable=False)
    photo: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)

    local_contacts: Mapped[List['LocalContact']] = relationship(back_populates='expert')
    meetings: Mapped[List['Meeting']] = relationship(back_populates='expert')

    topics: Mapped[List['Topic']] = relationship(secondary=expert_topic_association_table, back_populates='experts')


class Statistic(PostgresBase):
    __tablename__ = 'statistic'

    user_id = mapped_column(BigInteger(), primary_key=True)
    last_activity_date = mapped_column(DateTime(timezone=True), nullable=False)
    last_pressed_button: Mapped[str] = mapped_column(nullable=False)
    presses: Mapped[int] = mapped_column(default=0, nullable=False)


class Topic(PostgresBase):
    __tablename__ = 'topic'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    applicants: Mapped[List['Applicant']] = relationship(
        secondary=applicant_topic_association_table,
        back_populates='topics'
    )
    experts: Mapped[List['Expert']] = relationship(secondary=expert_topic_association_table, back_populates='topics')


class Meeting(PostgresBase):
    __tablename__ = 'meeting'

    id: Mapped[int] = mapped_column(primary_key=True)
    api_id = mapped_column(BigInteger(), nullable=False)
    date = mapped_column(DateTime(timezone=True), nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)
    expert_feedback = mapped_column(Text())
    applicant_feedback = mapped_column(Text())
    expert_confirmed: Mapped[bool]
    applicant_confirmed: Mapped[bool]
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    applicant_id = mapped_column(ForeignKey('applicant.id'))
    expert_id = mapped_column(ForeignKey('expert.id'))

    applicant: Mapped['Applicant'] = relationship(back_populates='meetings')
    expert: Mapped['Expert'] = relationship(back_populates='meetings')

    notifications: Mapped[List['Notification']] = relationship(back_populates='meeting')


class LocalContact(PostgresBase):
    __tablename__ = 'local_contact'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    expert_id = mapped_column(ForeignKey('expert.id'))
    applicant_id = mapped_column(ForeignKey('applicant.id'))

    applicant: Mapped['Applicant'] = relationship(back_populates='local_contacts')
    expert: Mapped['Expert'] = relationship(back_populates='local_contacts')


class Notification(PostgresBase):
    __tablename__ = 'notification'

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    meeting_id = mapped_column(ForeignKey('meeting.id'))

    meeting: Mapped['Meeting'] = relationship(back_populates='notifications')


class Migration(PostgresBase):
    __tablename__ = '_migration'

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(default=0, nullable=False)
