from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast1.database import get_session
from fast1.models import User
from fast1.schemas import Message, UserPublic, UserSchema, UsersList

app = FastAPI()

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Servidor rodando'}


@app.get('/exercicio-html', response_class=HTMLResponse)
def read_html():
    return """
    <html>
        <head>
            <title>Um olá mundo!</title>
            <body>
                <h1>Olá mundooooo! Hozier é maravilhoso</h1>
            </body>
        </head>
    </html>
"""


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username alread exists',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already exists'
            )
    db_user = User(
        username=user.username, password=user.password, email=user.email
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users', status_code=HTTPStatus.OK, response_model=UsersList)
def get_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_one_user(user_id: int, session: Session = Depends(get_session)):
    if user_id < 0:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='User id not valid')
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')
    return user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    db_user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    db_user.username == user.username
    db_user.password == user.password
    db_user.email == user.email
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User not valid'
        )

    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return {'message': 'User deleted'}
