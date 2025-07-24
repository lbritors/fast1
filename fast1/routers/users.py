from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fast1.auth import get_current_user, hash_password
from fast1.database import get_session
from fast1.models import User
from fast1.schemas import (
    FilterPage,
    Message,
    UserPublic,
    UserSchema,
    UsersList,
)

Session_DB = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session_DB):

    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) |
            (User.email == user.email)
        )
    )
    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User or email already exists',
        )
    hash = hash_password(user.password)

    db_user = User(
        username=user.username, password=hash, email=user.email
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UsersList)
async def get_users(session: Session_DB,
            filter_users: Annotated[FilterPage, Query()]):

    query = await session.scalars(select(User).offset(filter_users.offset)
                            .limit(filter_users.limit))
    users = query.all()
    return {'users': users}


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
async def get_one_user(user_id: int, session: Session_DB):
    if user_id < 0:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='User id not valid')
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')
    return user


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int, user: UserSchema, session: Session_DB,
    current_user: Current_User
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='No permission'
        )

    query = select(User).where(
        and_(
            or_(User.username == user.username,
            User.email == user.email),
            User.id != current_user.id
        )
    )
    result = await session.execute(query)
    exist = result.scalar_one_or_none()
    if exist:
        raise HTTPException(
        status_code=HTTPStatus.CONFLICT,
        detail='User already exists'
    )

    current_user.username = user.username
    current_user.password = hash_password(user.password)
    current_user.email = user.email
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
async def delete_user(user_id: int, session: Session_DB,
                current_user: Current_User):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='No permission'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
