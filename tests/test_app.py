from http import HTTPStatus

from fastapi.testclient import TestClient

from fast1.app import app


def test_root_deve_retornar_ok_e_servidor_rodando():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Servidor rodando'}


def test_exercicio_html_retornar_ola_mundo_em_html():
    client = TestClient(app)

    response = client.get('/exercicio-html')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>Olá mundooooo! Hozier é maravilhoso</h1>' in response.text
