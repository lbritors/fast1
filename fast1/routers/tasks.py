from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast1.auth import get_current_user
from fast1.database import get_session
from fast1.models import Task, User
from fast1.schemas import (
    TaskFilter,
    TaskList,
    TasksCreate,
    TasksRead,
    TasksUpdate,
)

router = APIRouter(prefix='/tasks', tags=['tasks'])


Session_DB = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TasksRead)
async def create_task(task: TasksCreate, user: Current_User,
                      session: Session_DB):

    task_db = Task(
        name=task.name,
        description=task.description,
        state=task.state,
        user_id=user.id
    )

    session.add(task_db)
    await session.commit()
    await session.refresh(task_db)

    return task_db


@router.get('/', status_code=HTTPStatus.OK, response_model=TaskList)
async def get_tasks(user: Current_User, session: Session_DB,
                    task_filter: Annotated[TaskFilter, Query()]):

    query = select(Task).where(Task.user_id == user.id)

    if task_filter.name:
        query = query.filter(Task.name.contains(task_filter.name))

    if task_filter.description:
        query = query.filter(Task.description.
                             contains(task_filter.description))

    if task_filter.state:
        query = query.filter(Task.state == task_filter.state)

    tasks = await session.scalars(query.offset(task_filter.offset).
                                  limit(task_filter.limit))

    return {'tasks': tasks.all()}


@router.get('/{task_id}', status_code=HTTPStatus.OK, response_model=TasksRead)
async def get_one_task(task_id: int, user: Current_User, session: Session_DB):

    query = select(Task).where(
        Task.user_id == user.id,
        Task.id == task_id)

    task = await session.scalar(query)
    if not task:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Not found')
    return task


@router.patch('/{task_id}', status_code=HTTPStatus.OK,
               response_model=TasksRead)
async def update_task(task_id: int, user: Current_User, session: Session_DB,
                      task: TasksUpdate):

    db_task = await session.scalar(select(Task).where(Task.user_id == user.id,
                                                      Task.id == task_id))

    if not db_task:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Not found'
        )

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)

    return db_task
