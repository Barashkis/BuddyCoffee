import base64
import time
import json
from functools import lru_cache

import requests

from config import ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
from loader import tz
from my_logger import logger


def get_ttl_hash(seconds=3600):
    return round(time.time() / seconds)


@lru_cache()
def generate_token(ttl_hash=None):
    del ttl_hash

    body = {
        "account_id": ZOOM_ACCOUNT_ID,
        "grant_type": "account_credentials",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}".encode()).decode(),
        "Host": "zoom.us",
    }
    resp = requests.post(
        "https://zoom.us/oauth/token",
        headers=headers,
        data=body,
    )
    resp_data = json.loads(resp.text)

    return resp_data["access_token"]


def create_meeting(start_time):
    body = {
        "topic": "Встреча со специалистом Росатома",
        "type": 2,
        "start_time": start_time,
        "duration": "40",
        "timezone": tz,
        "agenda": "Встреча со специалистом Росатома",
    }
    headers = {
        "Authorization": "Bearer " + generate_token(),
        "Content-Type": "application/json",
    }
    resp = requests.post(
        "https://api.zoom.us/v2/users/me/meetings",
        headers=headers,
        data=json.dumps(body),
    )
    resp_data = json.loads(resp.text)
    join_url = resp_data["join_url"]
    api_id = resp_data["id"]

    logger.debug(f"Script generated new zoom meeting link arranged at {start_time}")

    return join_url, api_id


def update_meeting_date(api_id, new_start_time):
    body = {"start_time": new_start_time}
    headers = {
        "Authorization": "Bearer " + generate_token(),
        "Content-Type": "application/json",
    }
    requests.patch(
        f"https://api.zoom.us/v2/meetings/{api_id}",
        headers=headers,
        data=body,
    )

    logger.debug(f"Script updated meeting with api_id {api_id} to date {new_start_time}")
