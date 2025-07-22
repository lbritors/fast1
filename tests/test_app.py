from http import HTTPStatus

from fast1.auth import create_access_token


def test_root_deve_retornar_ok_e_servidor_rodando(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Servidor rodando'}


def test_exercicio_html_retornar_ola_mundo_em_html(client):
    response = client.get('/exercicio-html')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>Olá mundooooo! Hozier é maravilhoso</h1>' in response.text


def test_login(client, user):
    response = client.post(
        '/login',
        data={'username': user.email, 'password': user.plain_password}
    )

    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_create_user(client):
    response = client.post(
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


def test_create_user_that_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'luna',
            'email': 'luna@luna.com',
            'password': '123'
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User or email already exists'}


def test_get_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_one_user(client, user):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'luna',
        'email': 'luna@luna.com',
    }


def test_get_one_user_id_le_zero(client):
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user, token):
    response = client.put(
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


def test_update_user_already_exists(client, user, token):
    response = client.post(
       f'/users/{user.id}',
       headers={'Authorization': f'Bearer {token}'},
       json={
           'username': 'teste',
           'email': 'luna@luna.com',
           'password': '123'
       }
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert response.json() == {'detail': 'Method Not Allowed'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_invalid_jwt_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_email_not_sent_jwt_token(client):
    data = {'no-email': 'teste'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_user_email_doesnt_exist(client):
    data = {'sub': 'let@let.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
