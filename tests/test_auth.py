from http import HTTPStatus

import pytest
from freezegun import freeze_time
from jwt import decode

from fast1.auth import create_access_token, settings


@pytest.mark.asyncio
async def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY,
                      algorithms=[settings.ALGORITHM])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


@pytest.mark.asyncio
async def test_invalid_jwt_token(client):
    response = await client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_login(client, user):
    response = await client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.plain_password}
    )

    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


@pytest.mark.asyncio
async def test_token_expired_after_time(client, user):
    with freeze_time('2025-07-24 12:00:00'):
        response = await client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.plain_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-24 12:31:00'):
        response = await client.put(
            f'/users/{user.id}',
            headers={'Authentication': f'Bearer {token}'},
            json={
                'username': 'wrong',
                'email': 'wrong@w.com',
                'password': '123'
            }
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_token_user_doesnt_exits(client):
    response = await client.post(
        '/auth/login',
        data={
            'username': 'none',
            'email': 'none@no.com',
            'password': '123'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_token_wrong_password(client, user):
    response = await client.post(
        '/auth/login',
        data={'username': user.email, 'password': 'wrong'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_refresh_token(client, user, token):
    response = await client.post(
        '/auth/refresh-token',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_token_expired_dont_refresh(client, user):
    with freeze_time('2025-07-24 12:00:00'):
        response = await client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.plain_password}
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-24 12:31:00'):
        response = await client.post(
            '/auth/refresh-token',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
