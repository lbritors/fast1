from http import HTTPStatus

import factory.fuzzy
import pytest

from fast1.models import Task, TaskState


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    name = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TaskState)
    user_id = 1


@pytest.mark.asyncio
async def test_create_task(client, token):
    response = await client.post(
        '/tasks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'hoje',
            'description': 'exercicios',
            'state': 'todo',
            'user_id': 1
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'hoje',
        'description': 'exercicios',
        'state': 'todo',
        'user_id': 1
    }


@pytest.mark.asyncio
async def test_get_tasks(client, token):
    response = await client.get(
        '/tasks/',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'tasks': []}


@pytest.mark.asyncio
async def test_get_five_tasks(client, token, session, user):
    tasks_qnt = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        '/tasks/',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == tasks_qnt


@pytest.mark.asyncio
async def test_get_tasks_pagination_equal_two(client, token, session,
                                              user):
    pag_qnt = 2
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        '/tasks/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == pag_qnt


@pytest.mark.asyncio
async def test_get_tasks_filter_should_return_5_tasks(
    client, session, token, user
):
    tasks_qnt = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id,
                                              name='estudar'))
    await session.commit()

    response = await client.get(
        '/tasks/?name=estudar',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == tasks_qnt


@pytest.mark.asyncio
async def test_get_tasks_filter_should_return_description_e(
    client, session, user, token
):
    tasks_qnt = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id,
                                             description='tomar 5 garrafas'))

    await session.commit()
    response = await client.get(
        '/tasks/?description=tomar 5',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == tasks_qnt


@pytest.mark.asyncio
async def test_get_tasks_filter_should_return_state_e(
    client, session, user, token
):
    tasks_qnt = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id,
                                             state=TaskState.draft))
    await session.commit()

    response = await client.get(
        '/tasks/?state=draft',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == tasks_qnt


@pytest.mark.asyncio
async def test_get_tasks_filter_should_return_all_filters(
    client, session, token, user
):
    tasks_qnt = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id,
                                             name="exercicio",
                                             description='fazer polichinelo,',
                                             state=TaskState.todo))
    session.add_all(TaskFactory.create_batch(3, user_id=user.id,
            name='Other title',
            description='other description',
            state=TaskState.todo,
        )
    )
    await session.commit()
    response = await client.get(
        '/tasks/?name=exercicio&description=polich&state=todo',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == tasks_qnt


@pytest.mark.asyncio
async def test_get_one_task(client, session, token, user):

    session.add(TaskFactory.create(user_id=user.id,
                                   name='estudar',
                                   description='ler 2 cap',
                                   state=TaskState.doing))
    await session.commit()
    response = await client.get(
        '/tasks/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {
        'id': 1,
        'name': 'estudar',
        'description': 'ler 2 cap',
        'state': 'doing',
        'user_id': 1
    }


@pytest.mark.asyncio
async def test_update_task(client, session, token, user):
    task = TaskFactory(user_id=user.id)

    session.add(task)
    await session.commit()

    response = await client.patch(
        f'/tasks/{task.id}',
        json={'name': 'teste'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'teste'


@pytest.mark.asyncio
async def test_update_task_not_found(client, token):

    response = await client.patch(
        '/tasks/2',
        json={'name': 'teste'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not found'}


@pytest.mark.asyncio
async def test_delete_task(client, token, user, session):
    task = TaskFactory(user_id=user.id)

    session.add(task)
    await session.commit()

    response = await client.delete(
        f'/tasks/{task.id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task deleted'
    }


@pytest.mark.asyncio
async def test_delete_task_not_exist(client, token):
    response = await client.delete(
        '/tasks/2',
        headers={'Authorization': f'Bearer {token}'}
    )

    print(response.json())

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not found'}
