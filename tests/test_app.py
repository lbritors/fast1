from http import HTTPStatus


def test_root_deve_retornar_ok_e_servidor_rodando(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Servidor rodando'}


def test_exercicio_html_retornar_ola_mundo_em_html(client):
    response = client.get('/exercicio-html')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>Olá mundooooo! Hozier é maravilhoso</h1>' in response.text


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


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'luna',
            'email': 'luna@luna.com',
            'password': 'luna',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'luna',
        'email': 'luna@luna.com',
    }


def test_update_user_id_le_zero(client):
    response = client.put(
        '/users/0',
        json={'username': 'bot', 'email': 'bot@email.com', 'password': '123'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_id_le_zero(client, user):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User not valid'}
