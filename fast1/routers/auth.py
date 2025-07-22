from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast1.auth import (
    create_access_token,
    verify_password,
)
from fast1.database import get_session
from fast1.models import User
from fast1.schemas import Token

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)
):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                             detail='Incorrect email or password')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail='Incorrect email or password')

    token = create_access_token(data={'sub': user.email})

    return {'access_token': token, 'token_type': 'bearer'}
