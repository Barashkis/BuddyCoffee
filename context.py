from contextvars import ContextVar
from typing import Optional

from database import PostgresBase


USER_TABLE: ContextVar[Optional[PostgresBase]] = ContextVar("user_table")
