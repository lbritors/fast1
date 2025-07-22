import os
from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast1.database import get_session
from fast1.models import User

load_dotenv()

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

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


def get_current_user(
        session: Session = Depends(get_session),
        token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'})

    try:
        payload = decode(token, secret_key, algorithms=[algorithm])
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.scalar(
        select(User).where(User.email == subject_email)
    )
    if not user:
        raise credentials_exception

    return user


def hash_password(pwd: str):
    return pwd_context.hash(pwd)


def verify_password(plain_pwd: str, hashed_pwd: str):
    return pwd_context.verify(plain_pwd, hashed_pwd)
