from datetime import datetime
from loader import db, tz
from pytz import timezone


def track_user_activity(user_id, table, button):
    db.update_user(table, "last_activity_time", user_id, f"{datetime.now(timezone(tz)).strftime('%d.%m.%Y %H:%M:%S')}, "
                                                         f"кнопка {button}")
