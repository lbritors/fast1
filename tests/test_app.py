from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_root_deve_retornar_ok_e_servidor_rodando(client):
    response = await client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Servidor rodando'}
