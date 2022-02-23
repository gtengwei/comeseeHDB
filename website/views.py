## For creation of stuff that can be viewed on homepage
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import *
from . import db
import json

views = Blueprint('views', __name__)

## To be changed to placeholders/HDB flats
## To be completed
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
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

    return render_template("home.html", user=current_user)

## 
@views.route('/delete-review', methods=['POST'])
def delete_review():
    review = json.loads(request.data)
    reviewId = review['reviewId']
    review = Review.query.get(reviewId)
    if review:
        if review.user_id == current_user.id:
            db.session.delete(review)
            db.session.commit()

    return jsonify({})
