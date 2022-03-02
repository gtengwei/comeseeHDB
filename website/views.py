## For creation of stuff that can be viewed on homepage
from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from .models import *
from . import db
import json
import sqlite3

views = Blueprint('views', __name__)

## To be changed to placeholders/HDB flats
## To be completed
@views.route('/reviews', methods=['GET', 'POST'])
@login_required
def review():
    if request.method == 'POST':
        review = request.form.get('review')

        if len(review) < 1:
            flash('Review is too short!', category='error')
        elif len(review) > 500:
            flash('Review is too long! Maximum length for a review is 500 characters', category='error')
        else:
            new_review = Review(data=review, user_id=current_user.id)
            db.session.add(new_review)
            db.session.commit()
            flash('Review added!', category='success')

    return render_template("review.html", user=current_user)

## 
@views.route('/delete-review', methods=['GET','POST'])
def delete_review():
    review = json.loads(request.data)
    reviewId = review['reviewId']
    review = Review.query.get(reviewId)
    if review:
        if review.user_id == current_user.id:
            db.session.delete(review)
            flash('Review deleted!', category='success')
            db.session.commit()

    return jsonify({})


@views.route('/flat-details/<flatId>', methods=['GET', 'POST'])
@login_required
def flat_details(flatId):
    flat = Flat.query.filter_by(id=flatId).first_or_404()
    if request.method == 'POST':
        review = request.form.get('review')

        if len(review) < 1:
            flash('Review is too short!', category='error')
        elif len(review) > 500:
            flash('Review is too long! Maximum length for a review is 500 characters', category='error')
        else:
            new_review = Review(data=review, user_id=current_user.id, flat_id = flatId)
            db.session.add(new_review)
            db.session.commit()
            flash('Review added!', category='success')
    return render_template("flat_details.html", user=current_user, flat = flat)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        flash('Flat favourited!', category = 'success')
        user = request.form.get(current_user.id)
        flat = request.data
        new_favourites = Favourites(user_id = 1, flat_id = 0)
        db.session.add(new_favourites)
        db.session.commit()
    os.chdir("/Users/nanshiyuan/Documents/GitHub/website")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    myquery = ("SELECT id, street_name, resale_price,flat_type, storey_range FROM Flat;")
    c.execute(myquery)
    data=list(c.fetchall())

    return render_template('home.html', user=current_user,data=data[:15])

@views.route('/unfavourite', methods=['POST'])
def unfavourite():
    favourite = json.loads(request.data)
    print(request.data)
    print("next line")
    print(favourite)
    favouriteID = favourite['favouriteID']
    favourite = Favourites.query.get(favouriteID)
    if favourite:
        if favourite.user_id == current_user.id:
            db.session.delete(favourite)
            db.session.commit()
    return jsonify({})

@views.route('/favourite', methods=['POST'])
def favourite():
    flat = json.loads(request.data)
    flatID = flat['flatID']
    new_favourites = Favourites(user_id = current_user.id , flat_id = flatID)
    db.session.add(new_favourites)
    db.session.commit()
    return jsonify({})

@views.route('/api', methods=['GET', 'POST'])
def api():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    myquery = ("SELECT id, street_name, resale_price,flat_type, storey_range FROM Flat;")
    c.execute(myquery)
    data=list(c.fetchall())

    if request.args:
        index = int(request.args.get('index'))
        limit = int(request.args.get('limit'))
    
        return jsonify({'data': data[index:limit + index]})
    else:
        return jsonify({'data': data})


