import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# Read SQL data file for initializing the database
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


# Enhanced SQL Test Data
"""
INSERT INTO user (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79'),
  ('admin', 'pbkdf2:sha256:50000$AdminSecure123$abc123abc456abc789');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('First Post', 'This is the first post.', 1, '2023-11-13 10:00:00'),
  ('Second Post', 'Another sample post content.', 2, '2023-11-13 12:00:00');
"""


# Test application configuration
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


# Basic test for '/hello' endpoint
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'


# Enhanced test for user registration
def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'newuser', 'password': 'newpassword'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'newuser'",
        ).fetchone() is not None


# Test edge cases for user registration
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('user', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
    ('toolongusername'*5, 'test', b'Username is too long.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


# Login tests with various assertions
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


# Test login edge cases
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('nonexistent', 'test', b'Incorrect username.'),
    ('test', 'wrongpassword', b'Incorrect password.'),
    ('!@#$%', 'test', b'Incorrect username.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


# Test user logout functionality
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session


# Test access to restricted routes when not logged in
def test_access_restricted(client):
    response = client.get('/blog/create')
    assert response.status_code == 302  # Redirect to login
    assert 'auth/login' in response.headers['Location']
