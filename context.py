from contextvars import ContextVar
from typing import (
    Optional,
    Union,
)

from database import (
    Applicant,
    Expert,
)


USER_TABLE: ContextVar[Optional[Union[Applicant, Expert]]] = ContextVar("user_table", default=None)
