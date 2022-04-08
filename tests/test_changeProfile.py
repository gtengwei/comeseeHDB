from .conftest import *

# =============================== POSTAL CODE CHANGE TESTS ===============================

def test_same_postalCodeChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail, testingPassword)
        username = current_user.username
        old_pcd = current_user.postal_code

        sinceLastChange = calculate_time_difference(datetime.now(), current_user.postal_code_change)
        assert sinceLastChange >= 90, "less than 3 months from postal_code change"

        rv = client.post(url_for('user.change_postal_code', username=username),
        data={'password': testingPassword, 'postalCode': old_pcd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Postal code must be different from current postal code." in rv.data
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "change_postal_code.html"

def test_invalid_postalCodeChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail, testingPassword)
        username = current_user.username
        old_pcd = current_user.postal_code
        new_pcd = "82" # ===========> insert values that do not fall within 1-80 (e.g -1, 100)

        assert old_pcd != new_pcd , "attempt to change to same postal code"
        sinceLastChange = calculate_time_difference(datetime.now(), current_user.postal_code_change)
        assert sinceLastChange >= 90, "less than 3 months from postal_code change"

        rv = client.post(url_for('user.change_postal_code', username=username),
        data={'password': testingPassword, 'postalCode': new_pcd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"First two digits of postal code must be between 1 and 80" in rv.data
        assert current_user.postal_code != new_pcd
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "change_postal_code.html"

def test_valid_postalCodeChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail, testingPassword)
        username = current_user.username
        old_pcd = current_user.postal_code
        new_pcd = "19" # ========> change after each run, '19' or '38' or '75'
        
        assert old_pcd != new_pcd , "attempt to change to same postal code"
        sinceLastChange = calculate_time_difference(datetime.now(), current_user.postal_code_change)
        assert sinceLastChange >= 90, "less than 3 months from postal_code change"

        rv = client.post(url_for('user.change_postal_code', username=username),
        data={'password': testingPassword, 'postalCode': new_pcd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Postal Code changed successfully!" in rv.data
        assert current_user.postal_code == new_pcd
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "profile.html"

def test_early_postalCodeChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail, testingPassword)
        username = current_user.username
        old_pcd = current_user.postal_code
        new_pcd = "38" 
        
        assert old_pcd != new_pcd , "attempt to change to same postal code"
        sinceLastChange = calculate_time_difference(datetime.now(), current_user.postal_code_change)
        assert sinceLastChange < 90
        msg = "You can change your postal code again in " + str(90 - sinceLastChange) + " days."

        rv = client.post(url_for('user.change_postal_code', username=username),
        data={'password': testingPassword, 'postalCode': new_pcd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert bytes(msg, encoding='utf-8') in rv.data
        assert current_user.postal_code != new_pcd
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "change_postal_code.html"

# =============================== PASSWORD CHANGE TESTS ===============================

testingEmail2 = "yap.xuan.ying2001@gmail.com"
old_pwd = "password123" # after/before each run, if last testcase passed -> switch "pwdChange123" or "password123" around

def test_same_pwdChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail2, old_pwd)
        username = current_user.username

        rv = client.post(url_for('user.request_password_change', username=username),
        data={'username': username, 'currentPassword': old_pwd,'password1': old_pwd, 'password2': old_pwd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"New password must be different from current password." in rv.data

        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "request_password_change.html"

def test_invalid_pwdChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail2, old_pwd)
        username = current_user.username
        new_pwd = "pwd<8"

        rv = client.post(url_for('user.request_password_change', username=username),
        data={'username': username, 'currentPassword': old_pwd,'password1': new_pwd, 'password2': new_pwd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Password must be at least 8 characters." in rv.data
        assert check_password_hash(current_user.password, new_pwd) is False
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "request_password_change.html"

def test_mismatch_pwdChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail2, old_pwd)
        username = current_user.username
        new_pwd = "pwdChange$$"

        rv = client.post(url_for('user.request_password_change', username=username),
        data={'username': username, 'currentPassword': old_pwd,'password1': new_pwd[:8], 'password2': new_pwd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Passwords must match" in rv.data
        assert check_password_hash(current_user.password, new_pwd) is False
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "request_password_change.html"

def test_wrongCurrentPwd_pwdChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail2, old_pwd)
        username = current_user.username
        new_pwd = "pwdChange$$"

        rv = client.post(url_for('user.request_password_change', username=username),
        data={'username': username, 'currentPassword': old_pwd[:8],'password1': new_pwd, 'password2': new_pwd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Incorrect password, try again" in rv.data
        assert check_password_hash(current_user.password, new_pwd) is False
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "request_password_change.html"

def test_valid_pwdChange(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,testingEmail2, old_pwd)
        username = current_user.username
        new_pwd = "pwdChange123"

        rv = client.post(url_for('user.request_password_change', username=username),
        data={'username': username, 'currentPassword': old_pwd,'password1': new_pwd, 'password2': new_pwd}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Password changed successfully!" in rv.data
        assert check_password_hash(current_user.password, new_pwd) is True
        
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        assert template.name == "home.html"
        template, context = captured_templates[1]
        assert template.name == "profile.html"
