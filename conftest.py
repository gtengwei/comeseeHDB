import pytest
from website import create_app, db
from website.models import *
from flask import template_rendered
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from flask import url_for, request


# Run tests in a module - pytest test_mod.py
# Run tests in a directory - pytest directory/
# Test (1) Favourite (2) Sort (3) Search (4) Filter (5) Review

            
@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app()
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    _app.config["TESTING"] = True
    _app.testing = True

    # This creates an in-memory sqlite db
    # See https://martin-thoma.com/sql-connection-strings/
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    #setup
    with _app.app_context():
        db.create_all()
        user1 = User(email='yap.xuan.ying2001@gmail.com', username = 'WiseF00l', postal_code ='190001',
                password=generate_password_hash('since2001', method='sha256'), email_verified = 1)
        db.session.add(user1)
        db.session.commit()

    yield _app

    #clean up resources
    ctx.pop()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

def login(client, email, password):
    return client.post(url_for('auth.login'), data=dict(
        email=email,
        password=password
    ),follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

# Testing
def test_login(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        rv = login(client,"yap.xuan.ying2001@gmail.com", "since2001")

        # session is still accessible
        assert rv.status_code == 200
        assert current_user.is_authenticated
        assert current_user.email == "yap.xuan.ying2001@gmail.com"
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "home.html"

    # session is no longer accessible

# For Anonymous Users -> for now - it does not work for me(XUAN YING)
#def test_home_get(client, captured_templates) -> None:

def test_flatdetails_get(client, captured_templates) -> None:
    with client:
        rv = client.get('/flat-details/0')

        # Sanity checks - it would be a total surprise if this would not hold true
        assert rv.status_code == 200
        assert b"fuck this shit" in rv.data
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "flat_details.html"

        # Here I test the two values which are passed to the template:
        print(context.keys())
        assert context["flatId"] == 1

def test_sort_get(client, captured_templates) -> None:
    with client:
        rv = client.get('/sort/price_high')

        # Sanity checks - it would be a total surprise if this would not hold true
        assert rv.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "home.html" # not sort.html -> because it is not via a POST request on sort page

def test_search_get(client, captured_templates) -> None:
    with client:
        rv = client.get('/search/Punggol Walk')

        # Sanity checks - it would be a total surprise if this would not hold true
        assert rv.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "search.html"
