from conftest import *

def test_valid_login(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        rv = login(client,"yeophuenyeo@gmail.com", "password123")

        # session is still accessible
        assert rv.status_code == 200
        assert current_user.is_authenticated
        assert current_user.email == "yeophuenyeo@gmail.com"
        assert current_user.username == "checkValidLogin"
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "home.html"

def test_unverified_login(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        rv = login(client,"yap.xuan.ying2001@gmail.com", "password123")

        # session is still accessible
        assert rv.status_code == 200
        assert b"Please verify your email address first" in rv.data
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "login.html"

def test_invalid_login(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        rv = login(client,"invalid@gmail.com", "invalid123")

        # session is still accessible
        assert rv.status_code == 200
        assert b"Email does not exist" or b"Incorrect password, try again" in rv.data
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "login.html"

def test_emptyField_login(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        rv = login(client,"", "")

        # session is still accessible
        assert rv.status_code == 200
        assert b"Email does not exist" or b"Incorrect password, try again" in rv.data
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "login.html"