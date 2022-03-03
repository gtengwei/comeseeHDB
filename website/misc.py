## Helper functions for website
## To organise the code
from website import mail
from flask import flash, url_for
from flask_mail import Message as MailMessage
from random import randint
from .models import User
from . import db
from datetime import datetime

def checkPassword(password1, password2):
    if password1 != password2:
        flash('Passwords don\'t match.', category='error')
        return False
    elif len(password1) < 7:
        flash('Password must be greater than 6 characters.', category='error')
        return False
    return True

def checkSpecialSymbol(password):
    if not any(char.isdigit() and char.isupper() and char.islower and char in '!@#$%^&*()_+' for char in password):
        flash('Password must contain at least one number, one uppercase letter, one lowercase letter and a special symbol.',
         category='error')
        return False
    if not any(char.isupper() for char in password):
        flash('Password must contain at least one uppercase letter.', category='error')
        return False
    if not any(char.islower() for char in password):
        flash('Password must contain at least one lowercase letter.', category='error')
        return False
    if not any(char in '!@#$%^&*()_+' for char in password):
        flash('Password must contain at least one special character.', category='error')
        return False
    return True

def send_mail_password(user):
    token = user.get_token()
    msg = MailMessage("Password Reset Request",recipients = [user.email], sender = 'noreply@comeseeHDB.com')

    msg.body = f'''
    To reset your password, visit the following link:
    {url_for('auth.reset_token', token=token, _external=True)}
    This link will expire in 2 minutes.
    If you did not make this request, please ignore this email and no changes will be made.
    '''
    
    mail.send(msg)

def send_mail_verify(user):
    token = user.get_token()
    msg = MailMessage("Verify your email",recipients = [user.email], sender = 'noreply@comeseeHDB.com')

    msg.body = f'''
    To verify your email, visit the following link:
    {url_for('auth.verify_token', token=token, _external=True)}
    This link will expire in 2 minutes.
    If you did not make this request, please ignore this email.
    '''
    mail.send(msg)

def calculate_time_difference(current_datetime, datetime_to_compare):
    time_difference = current_datetime - datetime_to_compare
    return time_difference.days