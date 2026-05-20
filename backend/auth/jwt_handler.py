# create/verify tokens

from jose import jwt
from jose import JWTError

from datetime import datetime
from datetime import timedelta
import datetime as dt


SECRET_KEY = "super_secret_key"

ALGORITHM = "HS256"

TOKEN_EXPIRE_MINUTES = 60


def create_token(data: dict):

    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow() +
        timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None