from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast1.auth import get_current_user, hash_password
from fast1.database import get_session
from fast1.models import User
from fast1.schemas import Message, UserPublic, UserSchema, UsersList

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
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
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UsersList)
def get_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_one_user(user_id: int, session: Session = Depends(get_session)):
    if user_id < 0:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='User id not valid')
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')
    return user


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='No permission'
        )

    current_user.username = user.username
    current_user.password = hash_password(user.password)
    current_user.email = user.email
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='No permission'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}
