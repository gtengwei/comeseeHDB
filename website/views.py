# For creation of stuff that can be viewed on homepage
from cgi import print_exception
from flask import Blueprint, render_template, request, flash, jsonify, session, url_for, redirect
from flask_login import login_required, current_user
from .models import *
from . import db
import json
import sqlite3
import os
from pathlib import Path
from .misc import *
import itertools
import requests
from collections import defaultdict

views = Blueprint('views', __name__)
#url = url_for('static', filename='images/' + str(random.randint(1,10)) + '.jpg')
INDEX = 20  # Number of items to show on homepage


@views.route('/delete-review', methods=['GET', 'POST'])
def delete_review():
    review = json.loads(request.data)
    reviewId = review['reviewId']
    review = Review.query.get(reviewId)
    if review:
        if review.user_id == current_user.id:
            flatId = review.flat_id
            db.session.delete(review)
            db.session.commit()
    return jsonify({})

# Route for every flat


@views.route('/flat-details/<flatId>', methods=['GET', 'POST'])
def flat_details(flatId):
    flat = Flat.query.filter_by(id=flatId).first_or_404()
    #photo = view_image(flatId)

    latitude = str(flat.latitude)
    longitude = str(flat.longitude)
    
    url1 = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photo_reference="
    url2 = "&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"
    url_staticimage = []
    # if photo:
    #     length = len(photo)
    #     cur = 0
    #     url = []
    #     while (cur < length):
    #         if photo[cur] == 0:
    #             url.append("\static\logo.png")
    #         else:
    #             temp = url1 + photo[cur] + url2
    #             url.append(temp)
    #         cur = cur + 1

    # else:
    #     url_staticimage = "https://maps.googleapis.com/maps/api/streetview?size=300x200&location=" + \
    #         latitude+","+longitude + \
    #         "&fov=80&heading=70&pitch=0&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"
    #     url = [url_staticimage, url_staticimage, url_staticimage]

    if request.method == 'POST':
        review = request.form.get('review')
        reply = request.form.get('reply')
        if reply:
            parent_id = request.form.get('parent_id')
            if len(reply) < 1:
                flash('Reply is too short!', category='error')
            elif len(reply) > 500:
                flash(
                    'Reply is too long! Maximum length for a reply is 500 characters', category='error')
            elif str(current_user.postal_code) != flat.postal_sector:
                print(type(flat.postal_sector))
                flash(
                    'You cannot reply to this review! You can only reply to reviews in your own postal district!', category='error')
            else:
                new_reply = Review(
                    data=reply, user_id=current_user.id, flat_id=flatId, parent_id=parent_id)
                new_reply.save()
                # print(parent_path)
                flash('Reply added!', category='success')
        if review:
            if len(review) < 1:
                flash('Review is too short!', category='error')
            elif len(review) > 500:
                flash(
                    'Review is too long! Maximum length for a review is 500 characters', category='error')
            elif str(current_user.postal_code) != flat.postal_sector:
                print(type(flat.postal_sector))
                flash(
                    'You cannot review this flat! You can only review flats in your own postal district!', category='error')
            else:
                new_review = Review(
                    data=review, user_id=current_user.id, flat_id=flatId)
                new_review.save()
                flash('Review added!', category='success')
    amenity = get_amenity(flatId)
    # f = open('testing.json') #FOR TESTING CAUSE EXPENSIVE
    # amenity = json.load(f)
    # amenity = amenity
    
    # PAGINATION
    page = request.args.get('page', 1, type=int)
    review1 = Review.query.filter(Review.flat_id == flatId).order_by(Review.numOfParentLikes.desc()).paginate(page=page, per_page=10)
    # print(review1.items)
    temp = defaultdict(list)
    review2 = []
    
    for item in review1.items:
        comment = item.review_path.split(".")
        temp[int(comment[0])].append([item, len(comment), item.numOfLikes])

    for key, value in temp.items():
        value = sorted(value, key=lambda x: (x[1], -x[2]))
        # print(value)
        for item in value:
            review2.append(item[0])
    
    # print(review2)
    review1.items = review2
    # print(review1.items)
    return render_template("flat_details.html", user=current_user, flat=flat, amenities=amenity, latitude=latitude, longitude=longitude, review1=review1)

@views.route('/flat_like', methods=['POST'])
@login_required
def flat_like():
    flat = json.loads(request.data)
    flatID = flat['flatID']
    flat = Flat.query.get(flatID)
    new_likes = FlatLikes(user_id=current_user.id, flat_id=flatID)
    db.session.add(new_likes)
    flat.numOfLikes += 1
    db.session.commit()
    return jsonify({"like_count": len(flat.likes)})

@views.route('/flat_unlike', methods=['POST'])
@login_required
def flat_unlike():
    like = json.loads(request.data)
    flatID = like['likeID']
    flat = Flat.query.get(flatID)
    for like in current_user.likes:
        if like.flat_id == flatID:
            db.session.delete(like)
            flat.numOfLikes -= 1
            db.session.commit()
    return jsonify({"like_count": len(flat.likes)})

@views.route('/prop_like', methods=['POST'])
@login_required
def prop_like():
    prop = json.loads(request.data)
    propID = prop['propID']
    prop = Property.query.get(propID)
    new_likes = PropertyLikes(user_id=current_user.id, prop_id=propID)
    db.session.add(new_likes)
    prop.numOfLikes += 1
    db.session.commit()
    return jsonify({"like_count": len(prop.likes)})

@views.route('/prop_unlike', methods=['POST'])
@login_required
def prop_unlike():
    like = json.loads(request.data)
    propID = like['likeID']
    prop = Property.query.get(propID)
    for like in current_user.propertyLikes:
        if like.prop_id == propID:
            db.session.delete(like)
            prop.numOfLikes -= 1
            db.session.commit()
    return jsonify({"like_count": len(prop.likes)})


@views.route('/review_unlike', methods=['POST'])
@login_required
def review_unlike():
    like = json.loads(request.data)
    reviewID = like['reviewID']
    review = Review.query.get(reviewID)
    for review_like in current_user.review_likes:
        if review_like.review_id == reviewID:
            db.session.delete(review_like)
            if review.parent_id == None:
                review.numOfParentLikes -= 1
            review.numOfLikes -= 1
            db.session.commit()
    return jsonify({"review_like_count": len(review.likes)})

@views.route('/review_like', methods=['POST'])
@login_required
def review_like():
    review = json.loads(request.data)
    reviewID = review['reviewID']
    review = Review.query.get(reviewID)
    new_likes = ReviewLikes(
        user_id=current_user.id, review_id=reviewID)
    db.session.add(new_likes)
    if review.parent_id == None:
        review.numOfParentLikes += 1
    review.numOfLikes += 1
    db.session.commit()
    return jsonify({"review_like_count": len(review.likes)})


@views.route('/flat_like_count', methods=['POST'])
def flat_like_count():
    flat = json.loads(request.data)
    flatID = flat['flatID']
    flat = Flat.query.get(flatID)
    return jsonify({"like_count": len(flat.likes)})

@views.route('/prop_like_count', methods=['POST'])
def prop_like_count():
    prop = json.loads(request.data)
    propID = prop['propID']
    prop = Property.query.get(propID)
    return jsonify({"like_count": len(prop.likes)})


@views.route('/review_like_count', methods=['POST'])
def review_like_count():
    review = json.loads(request.data)
    reviewID = review['reviewID']
    review = Review.query.get(reviewID)
    return jsonify({"like_count": len(review.likes)})

# Route for Landing Page
@views.route('/', methods=['GET','POST'])
def landing():
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    return render_template("landing.html", user=current_user)

# Route for Home Page
@views.route('/home/', methods=['GET', 'POST'])
def home():
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    # print(os.getcwd())
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    myquery = (
        "SELECT id FROM Flat ORDER BY numOfLikes DESC;")
    c.execute(myquery)
    data = list(c.fetchall())
    # random.shuffle(data)
    RANDOM = generate_random_flat()
    data = data[:INDEX]

    # Search for flats from homepage
    if request.method == 'POST':
        price = request.form.getlist('price')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        address = request.form.get('search')
        session['price'] = price
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        session['amenities'] = amenities
        data = []
        # if address:
        #     address = "%{}%".format(address)
        return redirect(url_for('views.search', address=address, price=price, towns=towns, flat_types=flat_types, amenities=amenities))
        if price:
            price_range = [word for line in price for word in line.split('-')]
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i % 2 == 0:
                    data = list(itertools.chain(Flat.query.filter(
                        Flat.resale_price.between(price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all()))

            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)
            else:
                return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data), random=RANDOM)

        else:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)
            else:
                return render_template('search.html', user=current_user, flats=[], random=RANDOM)

    session.clear()
    # return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], likes = likes.query.all(), random = RANDOM, image = image, image_id = image_id)
    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in data], likes=FlatLikes.query.all(), random=RANDOM, image=[Flat.query.get(x).image for x in data])

@views.route('/home_property', methods=['GET', 'POST'])
@login_required
def home_property():
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    # print(os.getcwd())
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    myquery = (
        "SELECT id FROM Property ORDER BY numOfLikes DESC;")
    c.execute(myquery)
    data = list(c.fetchall())
    # random.shuffle(data)
    RANDOM = generate_random_property(data)
    data = data[:INDEX]

    # Search for flats from homepage
    if request.method == 'POST':
        price = request.form.getlist('price')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        address = request.form.get('search')
        session['price'] = price
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        data = []
        if address:
            address = "%{}%".format(address)

        if price:
            price_range = [word for line in price for word in line.split('-')]
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i % 2 == 0:
                    data = list(itertools.chain(Property.query.filter(
                        Property.price.between(price_range[i], price_range[i+1])).all()))

            if address and flat_types and towns:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address), Property.flat_type.in_(
                    flat_types), Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and towns:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address), Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and flat_types:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address), Property.flat_type.in_(
                    flat_types)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns and flat_types:
                searchedProps = Property.query.filter(Property.flat_type.in_(flat_types), Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns:
                searchedProps = Property.query.filter(Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif flat_types:
                searchedProps = Property.query.filter(Property.flat_type.in_(flat_types)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)
            
            else:
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

        else:
            if address and flat_types and towns:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address), Property.flat_type.in_(
                    flat_types), Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and towns:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address), Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address and flat_types:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address), Property.flat_type.in_(
                    flat_types)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif address:
                searchedProps = Property.query.filter(Property.address_no_postal_code.like(address)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns and flat_types:
                searchedProps = Property.query.filter(Property.flat_type.in_(flat_types), Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif towns:
                searchedProps = Property.query.filter(Property.town.in_(towns)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)

            elif flat_types:
                searchedProps = Property.query.filter(Property.flat_type.in_(flat_types)).all()
                data = [prop for prop in data if prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=len(data), random=RANDOM)
            
            else:
                searchedProps = Property.query.filter(Property.flat_type.in_(['2 ROOM'])).all()
                data = [print(prop) for prop in searchedProps]
                return render_template("search_property.html", user=current_user, property=data[:INDEX], data_length=0, random=RANDOM)

    session.clear()
    # return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], likes = likes.query.all(), random = RANDOM, image = image, image_id = image_id)
    return render_template('home_property.html', user=current_user, property=[Property.query.get(x) for x in data], random=RANDOM, flats=[Property.query.get(x) for x in data],)


# Infinite Scrolling for Home Page


@views.route('/load_home', methods=['GET', 'POST'])
def load_home():
    # In order to load sorted flats faster
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    criteria = session.get('criteria')
    if criteria:
        if criteria == 'price_high':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY resale_price DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_low':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY resale_price;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'remaining_lease_high':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY remaining_lease DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'remaining_lease_low':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY remaining_lease;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'storey_high':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY storey_range DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'storey_low':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY storey_range;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'price_per_sqm_high':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY price_per_sqm DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'price_per_sqm_low':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY price_per_sqm;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'likes_high':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY numOfLikes DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'likes_low':
            myquery = (
                "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY numOfLikes;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                data = data[index:limit + index]
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).likes))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

    else:
        myquery = (
            "SELECT id, address_no_postal_code, resale_price,flat_type, storey_range, image, month FROM Flat ORDER BY numOfLikes DESC;")
        c.execute(myquery)
        data = list(c.fetchall())
        # random.shuffle(data)

        if request.args:
            index = int(request.args.get('index'))
            limit = int(request.args.get('limit'))

            data = data[index:limit + index]
            for x in range(len(data)):
                tuple_x = data[x]
                list_x = list(tuple_x)
                flat_id = list_x[0]
                list_x.append(len(Flat.query.get(flat_id).likes))
                tuple_x = tuple(list_x)
                data[x] = tuple_x

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})


# Route for Searching flats
@views.route('/search/', methods=['GET', 'POST'])
def search():
    RANDOM = generate_random_flat()
    if request.method == 'POST':
        price = request.form.getlist('price')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        if price:
            price = ','.join(price)
        if towns:
            towns = ','.join(towns)
        if flat_types:
            flat_types = ','.join(flat_types)
        if amenities:
            amenities = ','.join(amenities)

        address = request.form.get('search')
        if address == '':
            address = None
        session['price'] = price
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        session['amenities'] = amenities
        return redirect(url_for('views.search', address=address, flat_types=flat_types, towns=towns, amenities=amenities, price=price))
    
    searched_flats_address = None
    searched_flats_flat_types = None
    searched_flats_towns = None
    searched_flats_amenities = None
    searched_flats_price = None
    searched_flats = []
    
    address = request.args.get('address')
    flat_types = request.args.get('flat_types')
    towns = request.args.get('towns')
    amenities = request.args.get('amenities')
    price = request.args.get('price')
    print(address, flat_types, towns, amenities, price)
    
    
    if address:
        address = "%{}%".format(address)
        searched_flats_address = Flat.query.filter(Flat.address_no_postal_code.like(address)).all()
        searched_flats.append(searched_flats_address)
    if flat_types:
        flat_types = flat_types.split(',')
        searched_flats_flat_types = Flat.query.filter(Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
        searched_flats.append(searched_flats_flat_types)
    if towns:
        towns = towns.split(',')
        searched_flats_towns = Flat.query.filter(Flat.town.in_(towns)).all()
        searched_flats.append(searched_flats_towns)
    if amenities:
        amenities = amenities.split(',')
        searched_flats_amenities = Flat.query.filter(Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
        searched_flats.append(searched_flats_amenities)
    if price:
        price = price.split(',')
        price_range = [word for line in price for word in line.split('-')]
        print(price_range)
        for i in range(len(price_range)):
            price_range[i] = int(price_range[i])
            if i % 2 == 0:
                searched_flats_price = list(itertools.chain(Flat.query.filter(
                    Flat.resale_price.between(price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all()))
                # print(searched_flats_price)
        searched_flats.append(searched_flats_price)
    searched_flats = [i for i in searched_flats if i is not None]
    print(len(searched_flats))
    searched_flats = list(set.intersection(*map(set, searched_flats)))
    
    # searched_flats = searched_flats.order_by(Flat.month.desc()).all()
    # print(searched_flats)
    searched_flats.sort(key=lambda x: x.month, reverse=True)
    return render_template("search.html", user=current_user, flats=searched_flats[:INDEX], data_length=len(searched_flats))
    if request.method == 'POST':
        price = request.form.getlist('price')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        address = request.form.get('search')
        session['price'] = price
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        session['amenities'] = amenities
        if address:
            address = "%{}%".format(address)

        if price:
            data = []
            price_range = [word for line in price for word in line.split('-')]
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i % 2 == 0:
                    data = list(itertools.chain(Flat.query.filter(
                        Flat.resale_price.between(price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all()))

            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                data = [flat for flat in data if flat in searchedFlats]

            return render_template("search.html", user=current_user, flats=data[:INDEX], data_length=len(data))

        else:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX], data_length=len(searchedFlats), random=RANDOM)

            else:
                return render_template("search.html", user=current_user, flats=[], data_length=len(data))

    return render_template('search.html', user=current_user, address=address, random=RANDOM)


# Infinite Scrolling for Search Page
@views.route('/load_search', methods=['GET', 'POST'])
def load_search():
    data = []
    data_price = []
    price = session.get('price')
    address = session.get('address')
    towns = session.get('towns')
    flat_types = session.get('flat_types')
    amenities = session.get('amenities')
    if address:
        address = "%{}%".format(address)

    if price:
        price_range = [word for line in price for word in line.split('-')]
        for i in range(len(price_range)):
            price_range[i] = int(price_range[i])
            if i % 2 == 0:
                data_price = list(itertools.chain(Flat.query.filter(
                    Flat.resale_price.between(price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all()))

        if address and flat_types and amenities and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address and towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address and towns and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address and towns:
            searchedFlats = Flat.query.filter(
                Flat.address.like(address), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif address:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif towns and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif towns and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif towns:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif flat_types:
            searchedFlats = Flat.query.filter(
                Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

        elif amenities:
            searchedFlats = Flat.query.filter(
                Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]

    else:
        if address and flat_types and amenities and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()

        elif address and towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()

        elif address and towns and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

        elif address and towns:
            searchedFlats = Flat.query.filter(
                Flat.address.like(address), Flat.town.in_(towns)).order_by(Flat.month.desc()).all()

        elif address and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

        elif address and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()

        elif address and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

        elif address:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).order_by(Flat.month.desc()).all()

        elif towns and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

        elif towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()

        elif towns and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

        elif towns:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns)).order_by(Flat.month.desc()).all()

        elif flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

        elif flat_types:
            searchedFlats = Flat.query.filter(
                Flat.flat_type.in_(flat_types)).order_by(Flat.month.desc()).all()

        elif amenities:
            searchedFlats = Flat.query.filter(
                Flat.amenities.in_(amenities)).order_by(Flat.month.desc()).all()

    if data_price:
        for flat in data_price:
            data.append(tuple([flat.id, flat.address_no_postal_code,
                               flat.resale_price, flat.flat_type, flat.storey_range, flat.image, flat.month]))
    else:
        for flat in searchedFlats:
            data.append(tuple([flat.id, flat.address_no_postal_code,
                               flat.resale_price, flat.flat_type, flat.storey_range, flat.image, flat.month]))
    if request.args:
        index = int(request.args.get('index'))
        limit = int(request.args.get('limit'))
        data = data[index:limit + index]
        for x in range(len(data)):
            tuple_x = data[x]
            list_x = list(tuple_x)
            flat_id = list_x[0]
            list_x.append(len(Flat.query.get(flat_id).likes))
            tuple_x = tuple(list_x)
            data[x] = tuple_x

        return jsonify({'data': data})
    else:
        return jsonify({'data': data})


# Route for Sorting
@views.route('/sort/<criteria>', methods=['GET', 'POST'])
def sort(criteria):
    # If user searches from sort page
    RANDOM = generate_random_flat()
    data = []
    if request.method == 'POST':
        price = request.form.getlist('price')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        address = request.form.get('search')
        session['price'] = price
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        session['amenities'] = amenities
        if address:
            address = "%{}%".format(address)

        if price:
            price_range = [word for line in price for word in line.split('-')]
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i % 2 == 0:
                    data.extend(Flat.query.filter(Flat.resale_price.between(
                        price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all())

            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            return sorting_criteria(criteria, data)

        elif not price:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).all()

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).all()

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).all()

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).all()

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).all()

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).all()

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).all()
            else:
                searchedFlats = []
            return sorting_criteria(criteria, searchedFlats)

    # User did not search or filter from sort page, hence we will use the session information to sort
    else:
        price = session.get('price')
        address = session.get('address')
        towns = session.get('towns')
        flat_types = session.get('flat_types')
        amenities = session.get('amenities')

        if address:
            address = "%{}%".format(address)

        if price:
            price_range = [word for line in price for word in line.split('-')]
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i % 2 == 0:
                    data.extend(Flat.query.filter(Flat.resale_price.between(
                        price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all())

            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]

            else:
                return sorting_criteria(criteria, data)

            return sorting_criteria(criteria, data)

        elif not price:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address and towns:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address), Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif address:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(
                    towns), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                    flat_types), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif flat_types:
                searchedFlats = Flat.query.filter(
                    Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif amenities:
                searchedFlats = Flat.query.filter(
                    Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif not address and not towns and not flat_types and not amenities:
                # no sort or filter or search
                cwd = Path(__file__).parent.absolute()
                os.chdir(cwd)
                conn = sqlite3.connect("database.db")
                c = conn.cursor()

                if criteria == 'price_high':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY resale_price DESC;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'price_low':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY resale_price;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
                elif criteria == 'remaining_lease_high':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY remaining_lease DESC;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'remaining_lease_low':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY remaining_lease;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'storey_high':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY storey_range DESC;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'storey_low':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY storey_range;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'price_per_sqm_high':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY price_per_sqm DESC;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'price_per_sqm_low':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY price_per_sqm;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'likes_high':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY numOfLikes DESC;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)
                elif criteria == 'likes_low':
                    myquery = (
                        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY numOfLikes;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x], random=RANDOM)

    return render_template('sort.html', user=current_user)


# Infinite Scrolling for Sort Page
@views.route('/load_sort', methods=['GET', 'POST'])
def load_sort():
    data = []
    price = session.get('price')
    criteria = session.get('criteria')
    address = session.get('address')
    flat_types = session.get('flat_types')
    amenities = session.get('amenities')
    towns = session.get('towns')
    if address:
        address = '%{}%'.format(address)

    if price:
        data = []
        price_range = [word for line in price for word in line.split('-')]
        for i in range(len(price_range)):
            price_range[i] = int(price_range[i])
            if i % 2 == 0:
                data.extend(Flat.query.filter(Flat.resale_price.between(
                    price_range[i], price_range[i+1])).order_by(Flat.month.desc()).all())
        if flat_types:
            searchedFlats = Flat.query.filter(
                Flat.flat_type.in_(flat_types)).all()
            data = [flat for flat in data if flat in searchedFlats]

        if address and flat_types and amenities and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address and towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address and towns and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address and towns:
            searchedFlats = Flat.query.filter(
                Flat.address.like(address), Flat.town.in_(towns)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif address:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif towns and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.flat_type.in_(flat_types)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif towns and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif towns:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif flat_types:
            searchedFlats = Flat.query.filter(
                Flat.flat_type.in_(flat_types)).all()
            data = [flat for flat in data if flat in searchedFlats]

        elif amenities:
            searchedFlats = Flat.query.filter(
                Flat.amenities.in_(amenities)).all()
            data = [flat for flat in data if flat in searchedFlats]

        return sorting_criteria_load(criteria, data)

    else:
        if address and flat_types and amenities and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()

        elif address and towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()

        elif address and towns and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()

        elif address and towns:
            searchedFlats = Flat.query.filter(
                Flat.address.like(address), Flat.town.in_(towns)).all()

        elif address and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()

        elif address and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.flat_type.in_(flat_types)).all()

        elif address and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address), Flat.amenities.in_(amenities)).all()

        elif address:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).all()

        elif towns and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).all()

        elif towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.flat_type.in_(flat_types)).all()

        elif towns and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(
                towns), Flat.amenities.in_(amenities)).all()

        elif towns:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()

        elif flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(
                flat_types), Flat.amenities.in_(amenities)).all()

        elif flat_types:
            searchedFlats = Flat.query.filter(
                Flat.flat_type.in_(flat_types)).all()

        elif amenities:
            searchedFlats = Flat.query.filter(
                Flat.amenities.in_(amenities)).all()

        return sorting_criteria_load(criteria, searchedFlats)


# TESTING
# getting image (in flat details only)
def view_image(flatId):

    # find the name of the flat to find the place id
    flat = Flat.query.filter_by(id=flatId).first_or_404()
    flat = Flat.query.get(flatId)
    blk = flat.block
    street = flat.street_name

    name = blk + street + "hdb"

    while(name.find(' ') != -1):
        name = name.replace(' ', '%20')

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + \
        name + "&inputtype=textquery&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"

    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    if response['status'] != 'OK':
        return None
    else:
        primary = response['candidates'][0]
        id = primary['place_id']

        # finding photo reference
        url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + \
            id + "&fields=photos&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"

        payload = {}
        headers = {}

        response = requests.request(
            "GET", url, headers=headers, data=payload).json()
        res = response['result']
        photoRef = []
        cur = 0
        if 'photos' not in res:
            return photoRef
        photos = res['photos']
        noOfPhotos = len(photos)  # max number of photo references is 10
        cur = 0
        while (cur < noOfPhotos):
            temp1 = photos[cur]
            temp2 = temp1['photo_reference']
            photoRef.append(temp2)
            cur = cur + 1
        if len(photoRef) < 3:
            add = 3-len(photoRef)
            for i in range(add):
                photoRef.append(0)

        return photoRef


def get_amenity(flatId):
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)

    flat = Flat.query.filter_by(id=flatId).first_or_404()
    flat = Flat.query.get(flatId)
    latitude = flat.latitude
    longitude = flat.longitude
    address = flat.address
    filename = 'amenity_database.json'

    with open(filename, 'r') as f:
        data = json.load(f)
        if address in data.keys():
            return data.get(address)
        else:
            API_KEY = "AIzaSyAihwKNj-07whXNy0_nKDqkxN4QxCA-3uI"
            API_KEY2 = 'Ag6YKlKz_hSG8Drz9iLXx1n3-8r4qRW6XJSt2haPIuZr51AzdiGYq54G5amxfusp'

            specificamenity = {}  # specific amenity
            amenitydict = {}  # dictionaries of amenities
            amenity_list = ['bus_station', 'subway_station',
                            'school', 'restaurant', 'doctor']
            #amenity_list = ['school']
            for amenity in amenity_list:
                specificamenity = {}  # specific amenity
                url1 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + \
                    str(latitude) + "%2C" + str(longitude) + \
                    "&radius=500&type="+amenity+"&key=" + API_KEY
                payload = {}
                headers = {}

                response1 = requests.request(
                    "GET", url1, headers=headers, data=payload).json()
                length = response1["results"]
                for i in range(len(length)):
                    name = response1["results"][i]['name']
                    if len(name) > 30:
                        continue
                    if (amenity == 'school') and ('School' not in name):
                        continue
                    lat_of_nearby = response1['results'][i]['geometry']['location']['lat']
                    lon_of_nearby = response1['results'][i]['geometry']['location']['lng']
                    url2 = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins="+str(latitude)+","+str(longitude)+"&destinations="+str(lat_of_nearby)+"," + \
                        str(lon_of_nearby)+"&travelMode=walking&timeUnit=minute&distanceUnit=km&key=Ag6YKlKz_hSG8Drz9iLXx1n3-8r4qRW6XJSt2haPIuZr51AzdiGYq54G5amxfusp"
                    payload = {}
                    headers = {}
                    response2 = requests.request(
                        "GET", url2, headers=headers, data=payload).json()
                    nearby_distance = round((response2['resourceSets'][0]['resources'][0]
                                             ['results'][0]['travelDistance'])*1000)  # get distance in metres
                    nearby_duration = round(response2['resourceSets'][0]['resources']
                                            [0]['results'][0]['travelDuration'])  # get duration in minutes
                    specificamenity[name] = [nearby_distance, nearby_duration]
                    amenitydict[amenity] = specificamenity

                print(amenitydict)
        data[address] = amenitydict
        with open('amenity_database.json', 'w') as f:
            json.dump(data, f, indent=4)

    return amenitydict
