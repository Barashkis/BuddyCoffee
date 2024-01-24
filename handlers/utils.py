from datetime import datetime
from config import NEW_EVENT_MESSAGE
from loader import db, tz
from pytz import timezone


def build_applicant_menu_message_text():
    new_event_message_text = f"\n\n {NEW_EVENT_MESSAGE}" if NEW_EVENT_MESSAGE is not None else ""
    message_text = (
        "Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu" + new_event_message_text
    )

    return message_text


def track_user_activity(user_id, table, button):
    db.update_user(
        table,
        "last_activity",
        user_id,
        f"{datetime.now(tz=timezone(tz)).strftime('%d.%m.%Y %H:%M:%S')}, кнопка {button}",
    )
