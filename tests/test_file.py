import pytest

from io import StringIO, BytesIO

from raspberry.db import get_db

test_file = b'my file contents'
test_filename = 'test_file.txt'


def test_index(client, auth):
    response = client.get('/')
    assert b"Login" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\ndescription' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
        '/upload',
        '/1/update',
        '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    # change the file author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE file SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's file
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
        '/2/update',
        '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_upload(client, auth, app):
    auth.login()
    assert client.get('/upload').status_code == 200
    client.post('/upload', data={'title': 'created', 'description': 'by', 'file': (BytesIO(test_file), test_filename)})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM file').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'description': 'some description'})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM file WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


def test_create_validate(client, auth):
    auth.login()
    response = client.post('/upload',
                           data={
                               'title': '', 'description': 'by', 'file': (BytesIO(test_file), test_filename)
                           })
    assert b'Title is required.' in response.data

    response = client.post('/upload',
                           data={
                               'title': 'created', 'description': '', 'file': (BytesIO(test_file), test_filename)
                           })
    assert b'Description is required.' in response.data

    response = client.post('/upload', data={'title': 'created', 'description': 'by', 'file': ''})
    assert b'File is required.' in response.data

    response = client.post('/upload',
                           data={
                               'title': 'created', 'description': 'by', 'file': (BytesIO(test_file), 'test_file.xlsx')
                           })
    assert b'Invalid file format.' in response.data


def test_update_validate(client, auth):
    auth.login()
    response = client.post('/1/update', data={'title': 'a', 'description': ''})
    assert b'Description is required.' in response.data

    response = client.post('/1/update', data={'title': '', 'description': 'a'})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        file = db.execute('SELECT * FROM file WHERE id = 1').fetchone()
        assert file is None
