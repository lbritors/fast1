from http import HTTPStatus

from fastapi.testclient import TestClient

from fast1.app import app


def test_root_deve_retornar_ok_e_servidor_rodando():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Servidor rodando'}
