import json
from time import time

import jwt
import requests

from config import (
    zoom_api_key,
    zoom_api_secret,
)
from logger import logger
from services.meetings._base import Meeting


def zoom_auth_token():
    token = jwt.encode(
        {
            'iss': zoom_api_key,
            'exp': time() + 5000
        },
        zoom_api_secret,
        algorithm='HS256'
    )

    return token


class ZoomMeeting(Meeting):
    def __init__(self, start_time):
        self.start_time = start_time
        self.token = zoom_auth_token()

    def create(self, start_time):
        meeting_details = {
            'topic': 'Встреча со специалистом Росатома',
            'type': 2,
            'start_time': start_time,
            'duration': '40',
            'timezone': 'Europe/Moscow',
            'agenda': 'Встреча со специалистом Росатома',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': True,
                'jbh_time': 5,
                'waiting_room': False
            }
        }

        headers = {
            'authorization': 'Bearer ' + self.token,
            'content-type': 'application/json'
        }
        r = requests.post(
            'https://api.zoom.us/v2/users/me/meetings',
            headers=headers,
            data=json.dumps(meeting_details)
        )

        response = json.loads(r.text)
        join_url = response['join_url']
        api_id = response['id']

        logger.debug(f'Script generated new zoom meeting link arranged at {start_time}')

        return join_url, api_id

    def update_date(self, api_id, new_start_time):
        body = {
            'start_time': new_start_time
        }

        headers = {
            'authorization': 'Bearer ' + self.token,
            'content-type': 'application/json'
        }
        requests.patch(
            f'https://api.zoom.us/v2/meetings/{api_id}',
            headers=headers,
            data=json.dumps(body)
        )

        logger.debug(f'Script updated meeting with api_id {api_id} to date {new_start_time}')
