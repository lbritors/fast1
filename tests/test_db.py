from dataclasses import asdict

from sqlalchemy import select

from fast1.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='luna', password='123', email='luna@luna.com')
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'luna'))
    assert asdict(user) == {
        'id': 1,
        'username': 'luna',
        'password': '123',
        'email': 'luna@luna.com',
        'created_at': time,
        'updated_at': time,
    }
