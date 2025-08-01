from http import HTTPStatus

import pytest

from fast1.auth import create_access_token
from fast1.schemas import UserPublic
from tests.conftest import UserFactory


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        '/users/',
        json={
            'username': 'lorena',
            'email': 'lorena@email.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'lorena',
        'email': 'lorena@email.com',
    }


@pytest.mark.asyncio
async def test_create_user_that_already_exists(client, user: UserFactory):
    response = await client.post(
        '/users/',
        json={
            'username': user.username,
            'email': user.email,
            'password': user.password
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User or email already exists'}


@pytest.mark.asyncio
async def test_get_users(client):
    response = await client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


@pytest.mark.asyncio
async def test_get_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await client.get('/users/')
    assert response.json() == {'users': [user_schema]}


@pytest.mark.asyncio
async def test_get_one_user(client, user: UserFactory):
    response = await client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': user.username,
        'email': user.email,
    }


@pytest.mark.asyncio
async def test_get_one_user_id_le_zero(client):
    response = await client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_update_user(client, user, token):
    response = await client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'luna',
            'email': 'luna@luna.com',
            'password': 'luna',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'luna',
        'email': 'luna@luna.com',
    }


@pytest.mark.asyncio
async def test_update_user_already_exists(client, user: UserFactory,
                                        other_user: UserFactory, token):
    response = await client.put(
       f'/users/{user.id}',
       headers={'Authorization': f'Bearer {token}'},
       json={
           'username': user.username,
           'email': other_user.email,
           'password': user.password
       }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists'}


@pytest.mark.asyncio
async def test_update_user_with_wrong_id(client, user, token):
    response = await client.put(
        f'/users/{user.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'luna',
            'email': 'luna@luna.com',
            'password': '123'
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'No permission'}


@pytest.mark.asyncio
async def test_delete_user(client, user, token):
    response = await client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


@pytest.mark.asyncio
async def test_delete_user_wrong_id(client, other_user, token):
    response = await client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'No permission'}


@pytest.mark.asyncio
async def test_email_not_sent_jwt_token(client):
    data = {'no-email': 'teste'}
    token = create_access_token(data)

    response = await client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_user_email_doesnt_exist(client):
    data = {'sub': 'let@let.com'}
    token = create_access_token(data)

    response = await client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
