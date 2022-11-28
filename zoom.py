import jwt
import requests
import json
from time import time
from config import ZOOM_API_KEY, ZOOM_API_SEC

# create a function to generate a token
# using the pyjwt library
from my_logger import logger


def generate_token():
    token = jwt.encode(

        # Create a payload of the token containing
        # API Key & expiration time
        {'iss': ZOOM_API_KEY, 'exp': time() + 5000},

        # Secret used to generate token signature
        ZOOM_API_SEC,

        # Specify the hashing alg
        algorithm='HS256'
    )
    return token


# send a request with headers including a token and meeting details
def create_meeting(start_time):
    # create json data for post requests
    meetingdetails = {"topic": "Встреча со специалистом Росатома",
                      "type": 2,
                      "start_time": start_time,
                      "duration": "40",
                      "timezone": "Europe/Moscow",
                      "agenda": "Встреча со специалистом Росатома",
                      "settings": {"host_video": True,
                                   "participant_video": True,
                                   "join_before_host": True,
                                   "jbh_time": 5,
                                   "waiting_room": False
                                   }
                      }

    headers = {'authorization': 'Bearer ' + generate_token(),
               'content-type': 'application/json'}
    r = requests.post(
        f'https://api.zoom.us/v2/users/me/meetings',
        headers=headers, data=json.dumps(meetingdetails))
    # converting the output into json and extracting the details
    y = json.loads(r.text)
    join_url = y["join_url"]
    api_id = y["id"]
    # meetingPassword = y["password"]
    logger.debug(f"Script generated new zoom meeting link arranged at {start_time}")
    return join_url, api_id


def update_meeting_date(api_id, new_start_time):
    body = {
        "start_time": new_start_time
    }

    headers = {'authorization': 'Bearer ' + generate_token(),
               'content-type': 'application/json'}

    requests.patch(
        f'https://api.zoom.us/v2/meetings/{api_id}',
        headers=headers, data=json.dumps(body)
    )

    logger.debug(f"Script updated meeting with api_id {api_id} to date {new_start_time}")
