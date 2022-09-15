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
    meetingdetails = {"topic": "Встреча со специалистом РосАтома",
                      "type": 2,
                      "start_time": start_time,
                      "duration": "40",
                      "timezone": "Europe/Moscow",
                      "agenda": "Встреча со специалистом РосАтома",
                      "settings": {"host_video": True,
                                   "participant_video": True,
                                   "join_before_host": True,
                                   "jbh_time": 5,  # Doesn't work. Seems like there is problem on Zoom APi side...
                                   "waiting_room": False
                                   }
                      }

    headers = {'authorization': 'Bearer ' + generate_token(),
               'content-type': 'application/json'}
    r = requests.post(
        f'https://api.zoom.us/v2/users/me/meetings',
        headers=headers, data=json.dumps(meetingdetails))
    print(meetingdetails)
    # print(r.text)
    # converting the output into json and extracting the details
    y = json.loads(r.text)
    join_url = y["join_url"]
    # meetingPassword = y["password"]
    logger.debug(f"Script generated new zoom meeting link arranged at {start_time}")
    return join_url
