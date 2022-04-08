import pytest, sqlite3
from flask_sqlalchemy import SQLAlchemy
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, url_for, request, Blueprint, template_rendered
import sys
import os
sys.path.append("..")
from website import create_app, db
from website.misc import *
from website.models import *



# Run tests in a module - pytest tests/test_mod.py
# Run tests in a directory - pytest tests

testingEmail = "yeophuenyeo@gmail.com" # insert verified user email and password for testing
testingPassword = "password123"

            
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
    #_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.db" ====> cannot because for now, ourwebsite retrieves data from database.db [HARD-CODED in views.py]

    #setup ==> if not using database.db
    

    yield _app

    #clean up resources
    ctx.pop()

# HELPER METHODS ---------------------------------------
@pytest.fixture()
def client(app):
    with app.app_context():
        yield app.test_client()


@pytest.fixture()
def runner(app):
    with app.app_context():
        yield app.test_cli_runner()

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

