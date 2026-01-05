import time
import jwt
from dotenv import load_dotenv, set_key
import os

load_dotenv()

ak = os.getenv("KLING_ACCESS_KEY") # fill access key
sk = os.getenv("KLING_SECRET_KEY") # fill secret key

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 86400, # The valid time, in this example, represents the current time+1800s(30min)
        "nbf": int(time.time()) - 5 # The time when it starts to take effect, in this example, represents the current time minus 5s
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

authorization = encode_jwt_token(ak, sk)
# print(authorization) # Printing the generated API_TOKEN
# set_key(".env","KLING_API_KEY", authorization)
print(authorization)