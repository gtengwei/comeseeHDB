from conftest import *

def test_verified_sendVerification(client, captured_templates):

    with client:
        rv = client.post('/verify-email', 
        data={'email': 'yeophuenyeo@gmail.com'}, follow_redirects=True) # ==> insert verified email

        # session is still accessible
        assert rv.status_code == 200
        assert b"Email already verified. Please proceed to login!" in rv.data

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "login.html"

def test_unverified_sendVerification(client, captured_templates):

    with client:
        rv = client.post('/verify-email', 
        data={'email': 'yap.xuan.ying2001@gmail.com'}, follow_redirects=True) # ==> insert unverified email

        # session is still accessible
        assert rv.status_code == 200
        assert b"Verification email sent!" in rv.data

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "login.html"

def test_invalid_sendVerification(client, captured_templates):

    with client:
        rv = client.post('/verify-email', 
        data={'email': 'abc@gmail.com'}, follow_redirects=True) # ==> insert unregistered email or empty string

        # session is still accessible
        assert rv.status_code == 200
        assert b"Email does not exist" in rv.data

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "verify_email.html"