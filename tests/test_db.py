from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast1.models import Task, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='luna', password='123', email='luna@luna.com')
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'luna'))
    assert asdict(user) == {
        'id': 1,
        'username': 'luna',
        'password': '123',
        'email': 'luna@luna.com',
        'created_at': time,
        'updated_at': time,
        'tasks': [],
    }


@pytest.mark.asyncio
async def test_create_task(session, user):
    task = Task(
        name='teste',
        description='oi',
        state='todo',
        user_id=user.id
    )

    session.add(task)
    await session.commit()

    task = await session.scalar(select(Task))

    assert asdict(task) == {
        'id': 1,
        'name': 'teste',
        'description': 'oi',
        'state': 'todo',
        'user_id': 1
    }


@pytest.mark.asyncio
async def test_user_task_relationship(user: User, session):
    task = Task(
        name='task',
        description='do smt',
        state='todo',
        user_id=user.id
    )

    session.add(task)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.tasks == [task]
