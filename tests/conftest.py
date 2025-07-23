from contextlib import contextmanager
from datetime import datetime

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fast1.app import app
from fast1.auth import hash_password
from fast1.database import get_session
from fast1.models import User, table_registry


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 7, 15)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def client(session):
    app.dependency_overrides[get_session] = lambda: session

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def engine():
    """Cria um engine de teste que dura por toda a sessão de testes."""
    return create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )


@pytest_asyncio.fixture
async def session(engine):

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    password = '123'
    user = User(username='luna',
                email='luna@luna.com',
                password=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.plain_password = password
    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = await client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.plain_password},
    )

    return response.json()['access_token']
