## Everything related to the user
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from .misc import *

user = Blueprint('user', __name__)

## Route for every unique user
@user.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

## Request password change for every unique user
@user.route('/request-password-change/<username>', methods=['GET', 'POST'])
@login_required
def request_password_change(username):
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
        dummy = request.form.get('username')
        current_password = request.form.get('currentPassword')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if check_password_hash(user.password, current_password):

            if len(password1) < 8:
                flash('Password must be at least 8 characters.', category='error')
            elif password1 != password2:
                flash('Passwords must match.', category='error')
            
            elif current_password == password1:
                flash('New password must be different from current password.', category='error')
            else:
                user.password = generate_password_hash(password1)
                db.session.commit()
                flash('Password changed successfully!', category='success')
                return redirect(url_for('user.profile', username=username))
        else:
            flash('Incorrect password, try again.', category='error')

    
    return render_template("request_password_change.html", user=current_user)

## Change username for every unique user
@user.route('/change-username/<username>', methods=['GET', 'POST'])
@login_required
def change_username(username):
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
            username = request.form.get('username')
            check_username = User.query.filter_by(username=username).first()
            if username == current_user.username:
                flash('Username must be different from current username.', category='error')
            elif check_username:
                flash('Username already exists.', category='error')
            elif len(username) < 1:
                flash('Username must be at least 1 character long.', category='error')
            else:
                user.username = username
                db.session.commit()
                flash('Username changed successfully!', category='success')
                return redirect(url_for('user.profile', username=username))

    return render_template("change_username.html", user=current_user)


## Change postal code for every unique user
@user.route('/change-postal-code/<username>', methods=['GET', 'POST'])
@login_required
def change_postal_code(username):
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
            password = request.form.get('password')
            postal_code = request.form.get('postalCode')
            if check_password_hash(user.password, password):

                if (postal_code < str(1) or postal_code > str(80)):
                    flash('First two digits of postal code must be between 1 and 80.', category='error')

                elif (calculate_time_difference(datetime.now(), user.postal_code_change)) < 90 :
                    flash('You can only change your postal code 3 months after your last change.', category='error')
                    flash('You can change your postal code again in ' + str(90 - calculate_time_difference(datetime.now(), user.postal_code_change)) + ' days.', category='error')
                else:
                    user.postal_code = postal_code
                    user.postal_code_change = datetime.now()
                    db.session.commit()
                    flash('Postal Code changed successfully!', category='success')
                    return redirect(url_for('user.profile', username=username))
            else:
                flash('Incorrect password, try again.', category='error')

    return render_template("change_postal_code.html", user=current_user)

## Display favourites for every unique user
## To be completed
@user.route('/favourites/<username>', methods=['GET', 'POST']) 
@login_required
def favourites(username):
    fav_list = []
    for x in current_user.favourites:
            fav_list.append(x.flat_id)
    if request.method == 'POST':
        address = request.form.get('searchFavourites')
        print(address)
        address = "%{}%".format(address)
        flats = Flat.query.join(Favourites, Favourites.flat_id == Flat.id)\
        .filter(Favourites.user_id == current_user.id)\
        .filter(Flat.address.like(address)).all()
        if flats:
            return render_template("favourites.html", user=current_user, flats=flats)
        else:
            flash('No results found.', category='error')
            return render_template("favourites.html", user=current_user, flats=[])
            
    return render_template("favourites.html", user=current_user, flats = [Flat.query.get(x) for x in fav_list])





