## To create a new user in database and authenicate the user when they login
## For the definition of routes in the website
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message as MailMessage
from .misc import *
from datetime import datetime
import requests

auth = Blueprint('auth', __name__)

## Route for Login Page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if User.query.filter_by(email="test@gmail.com").first() is None:
        new_user = User(email = "test@gmail.com" ,
                        username = "12345678",
                        password = generate_password_hash("12345678", method="sha256"),
                        access_id = 0,
                        postal_code = 12,
                        email_verified = True,
                        email_verified_date = datetime.now())
        db.session.add(new_user)
        db.session.commit()
        print("test12345 added!")
        
    if User.query.filter_by(email="agent@gmail.com").first() is None:
        new_user = User(email = "agent@gmail.com" ,
                        username = "agent12345",
                        password = generate_password_hash("12345678", method="sha256"),
                        access_id = 1,
                        postal_code = 12,
                        email_verified = True,
                        email_verified_date = datetime.now())
        db.session.add(new_user)
        db.session.commit()
        print("agent12345 added!")
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()  
        if user:
            user_verify_email = User.query.filter_by(email=email).first().email_verified
            if user_verify_email == 0:
                flash('Please verify your email address first.', category='error')
                return redirect(url_for('auth.login'))
            elif check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('Email does not exist in the system. Please create an account before logging in!', category='error')

    return render_template("login.html", user=current_user)

## Route for Logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

## Route for Sign Up Page
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        if request.form.get('postalCode'):
            postal_code = int(request.form.get('postalCode'))
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        check_username = User.query.filter_by(username=username).first()
        if user:
            flash('Email already exists.', category='error')
        elif check_username:
            flash('Username already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')

        elif len(username) < 4:
            flash('Username must be at least 4 character long.', category='error')

        elif (postal_code < 1 or postal_code > 80):
            flash('First two digits of postal code must be between 1 and 80.', category='error')

        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')

        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')

        ## Need to add verification code/function here
        else:
            new_user = User(email=email, 
                            username = username, 
                            postal_code = postal_code,
                            access_id = 0,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            send_mail_verify(new_user)       
            flash('Account created! Please verify your email before logging in.', category='success')

            return redirect(url_for('auth.login'))
        
        

    return render_template("sign_up.html", user=current_user)

## Route for Agent Sign Up Page
@auth.route('/sign-up-for-agent', methods=['GET','POST'])
def sign_up_agent():
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username').upper()
        reg_no = request.form.get('reg_no')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #Check if the salesperson exists/active by using data.gov API
        url = f'https://data.gov.sg/api/action/datastore_search?resource_id=a41ce851-728e-4d65-8dc5-e0515a01ff31&limit=5&q={username}'
        response = requests.get(url)

        if response.status_code <= 200 & response.status_code >= 29:
            found = False
            result = response.json()['result']['records']
            for query in result:
                print(query['salesperson_name'], username)
                print( query['registration_no'], reg_no)
                if(username in query['salesperson_name'].upper() and query['registration_no'] == reg_no):
                    username = query['salesperson_name'].upper()
                    found = True

            if (not found):
                flash("Invalid Name and Registration Number!", category='error')
                return render_template("sign_up_agent.html", user=current_user)
        else:
            #If the data.gov API happens to be maintenancing
            flash('Encountered Unexpected Problem. Please try again after an hour!', category='error')
            return render_template("sign_up_agent.html", user=current_user)
        
        #Check if the information follows the requirements
        user = User.query.filter_by(email=email).first()
        check_username = User.query.filter_by(username=username).first()
        if user:
            flash('Email already exists.', category='error')
        elif check_username:
            flash('Username already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')

        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')

        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')

        
        else:
            new_agent = User(username = username,
                            email=email,
                            access_id = 1,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_agent)
            db.session.commit()
            send_mail_verify(new_agent)       
            flash('Please verify your email before logging in.', category='success')

            return redirect(url_for('auth.login'))
    return render_template("sign_up_agent.html", user=current_user)



## Route for Forgot Password Page
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_mail_password(user)
            flash('Password reset email sent!', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist.', category='error')

    return render_template("forgot_password.html", user=current_user)

## Route for Reset Password Page send to their email
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is an invalid or expired token', category='error')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')

        elif password1 != password2:
            flash('Password mismatch', category='error')

        password=generate_password_hash(password1, method='sha256')
        user.password = password
        db.session.commit()
        flash('Password Changed Successfully!', category='success')
        return redirect(url_for('auth.login'))
    
    return render_template("reset_password.html", user=current_user)


## Route for Verify Email
@auth.route('/verify-email/<token>')
def verify_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is an invalid or expired token', category='error')
        return redirect(url_for('auth.login'))
    
    elif user:
        user = User.query.filter_by(email=user.email).first()
        user.email_verified = True
        user.email_verified_date = datetime.now()
        db.session.commit()
        flash('Email Verified! You may proceed to login now.', category='success')
        return redirect(url_for('auth.login'))

    else:
         return render_template("login.html", user=current_user)


## Route for Send Email Verification
@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.email_verified == 1:
                flash('Email already verified. Please proceed to login!', category='error')
                return redirect(url_for('auth.login'))
            else:
                send_mail_verify(user)
                flash('Verification email sent!', category='success')
                return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist.', category='error')

    return render_template("verify_email.html", user=current_user)
