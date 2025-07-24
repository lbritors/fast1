from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast1.auth import create_access_token, get_current_user, verify_password
from fast1.database import get_session
from fast1.models import User
from fast1.schemas import Token

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session_DB = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/login', response_model=Token)
async def login(form_data: OAuth2Form,
          session: Session_DB
):
    user = await session.scalar(select(User).where(
        User.email == form_data.username
        ))
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                             detail='Incorrect email or password')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail='Incorrect email or password')

    token = create_access_token(data={'sub': user.email})

    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/refresh-token', response_model=Token)
async def refresh_token(user: CurrentUser):
    new_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_token, 'token_type': 'bearer'}
