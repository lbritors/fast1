from jwt import decode

from fast1.auth import create_access_token, secret_key


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, secret_key, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded
