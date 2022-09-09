from .conftest import *

'''
FLASH MESSAGES
    b"Email already exists."
    b"Username already exists."
    b"Email must be greater than 3 characters."
    b"Username must be greater than 1 character."
    b"First two digits of postal code must be between 1 and 80."
    b"Password must be at least 8 characters."
    b"Passwords don\'t match."
    b"Account created! Please verify your email before logging in."
'''

'''def test_valid_register(client, captured_templates):

    with client:
        rv = client.post('/sign-up', 
        data={'email': 'www.sherelyn912@gmail.com',
        'username': 'testValidRegister',
        'postalCode': '11',
        'password1': 'password123',
        'password2': 'password123'}, follow_redirects=True) #=====> insert email that has not been registered

        # session is still accessible
        assert rv.status_code == 200
        assert b"Account created! Please verify your email before logging in." in rv.data, "ensure email entered is not registered"
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "login.html"'''

def test_invalid_register(client, captured_templates):

    with client:
        rv = client.post('/sign-up', 
        data={'email': '',
        'username': 'testInvalidRegister',
        'postalCode': '111111',
        'password1': 'password123',
        'password2': 'password123'}) # incomplete email field

        # session is still accessible
        assert rv.status_code == 200
        assert b"Email must be greater than 3 characters." or b"Username must be greater than 1 character." or b"First two digits of postal code must be between 1 and 80." or b"Password must be at least 8 characters." or b"Passwords don\'t match." in rv.data

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "sign_up.html"

def test_existingKey_register(client, captured_templates):

    with client:
        rv = client.post('/sign-up', 
        data={'email': 'yeophuenyeo@gmail.com',
        'username': 'testExistingEmail',
        'postalCode': '111111',
        'password1': 'password123',
        'password2': 'password123'}) 

        # session is still accessible
        assert rv.status_code == 200
        assert b"Email already exists." in rv.data

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "sign_up.html"

