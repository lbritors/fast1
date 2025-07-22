from http import HTTPStatus

from jwt import decode

from fast1.auth import create_access_token, secret_key


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, secret_key, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_invalid_jwt_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_login(client, user):
    response = client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.plain_password}
    )

    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
