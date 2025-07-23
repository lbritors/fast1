from http import HTTPStatus

import pytest
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
