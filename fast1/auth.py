import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from jwt import encode
from pwdlib import PasswordHash

load_dotenv()

pwd_context = PasswordHash.recommended()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
expire_minutes = int(os.getenv("EXPIRE_MINUTES"))


def create_access_token(data: dict):

    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=expire_minutes
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt


def hash_password(pwd: str):
    return pwd_context.hash(pwd)


def verify_password(plain_pwd: str, hashed_pwd: str):
    return pwd_context.verify(plain_pwd, hashed_pwd)
