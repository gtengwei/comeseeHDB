# For creation of stuff that can be viewed on homepage
from cgi import print_exception
from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from .models import *
from . import db
import json
import sqlite3
import os
import random
from pathlib import Path
import mysql.connector
import pymysql
from .misc import *
import itertools

views = Blueprint('views', __name__)

INDEX = 20 # Number of items to show on homepage

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

# Route for every flat

@views.route('/flat-details/<flatId>', methods=['GET', 'POST'])
def flat_details(flatId):
    flat = Flat.query.filter_by(id=flatId).first_or_404()
    photo = view_image(flatId)

    url1 = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photo_reference="
    url2 = "&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"
    length = len(photo)
    cur = 0
    url = []
    while (cur < length):
        if photo[cur] == 0:
            url.append("\static\comeseeHDB logo.png")
        else:
            temp = url1 + photo[cur] + url2
            url.append(temp)
            cur = cur + 1

    
    if request.method == 'POST':
        review = request.form.get('review')

        if len(review) < 1:
            flash('Review is too short!', category='error')
        elif len(review) > 500:
            flash(
                'Review is too long! Maximum length for a review is 500 characters', category='error')
        else:
            new_review = Review(
                data=review, user_id=current_user.id, flat_id=flatId)
            db.session.add(new_review)
            db.session.commit()
            flash('Review added!', category='success')
    return render_template("flat_details.html", user=current_user, flat=flat, image = url)
    
@views.route('/unfavourite', methods=['POST'])
@login_required
def unfavourite():
    favourite = json.loads(request.data)
    flatID = favourite['favouriteID']
    flat = Flat.query.get(flatID)
    for favourite in current_user.favourites:
        if favourite.flat_id == flatID:
            db.session.delete(favourite)
            flat.numOfFavourites -= 1
            db.session.commit()
    return jsonify({"favourite_count": len(flat.favourites)})

@views.route('/favourite', methods=['POST'])
@login_required
def favourite():
    flat = json.loads(request.data)
    flatID = flat['flatID']
    flat = Flat.query.get(flatID)
    new_favourites = Favourites(user_id = current_user.id , flat_id = flatID)
    db.session.add(new_favourites)
    flat.numOfFavourites += 1
    db.session.commit()
    return jsonify({"favourite_count": len(flat.favourites)})
    
@views.route('/favourite_count', methods=['POST'])
def favourite_count():
    flat = json.loads(request.data)
    flatID = flat['flatID']
    flat = Flat.query.get(flatID)
    return jsonify({"favourite_count": len(flat.favourites)})

# Route for Home Page
@views.route('/', methods=['GET', 'POST'])
def home():
    cwd = Path(__file__).parent.absolute()
    print(cwd)
    os.chdir(cwd)
    #print(os.getcwd())
    conn = sqlite3.connect("database.db")
    #conn = pymysql.connect(host="localhost", user="root", passwd="Clutch123!", database="mysql_database")
    c = conn.cursor()
    myquery = (
        "SELECT id, address, resale_price,flat_type, storey_range FROM Flat;")
    c.execute(myquery)
    data = list(c.fetchall())
    # random.shuffle(data)
    
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
        if address:
            address = "%{}%".format(address)

        if price:
            #minPrice = int(price[0])
            #maxPrice = minPrice + 100000 
            price_range = [word for line in price for word in line.split('-')]
            print(price_range)
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i%2 == 0:
                    data = itertools.chain(Flat.query.filter(Flat.resale_price.between(price_range[i], price_range[i+1])).all())
                    #print(searchedFlats)
            #print(data[0])                
            #return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            else:
                return render_template("search.html", user=current_user, flats=data[:INDEX])

        else:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])

    session.clear()
    #return render_template('home.html', user=current_user, flats=data[:INDEX], favourites = Favourites.query.all())
    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in range(INDEX)], favourites = Favourites.query.all)





    
# Infinite Scrolling for Home Page
@views.route('/load_home', methods=['GET', 'POST'])
def load_home():

    ## In order to load sorted flats faster
    conn = sqlite3.connect("database.db")
    #conn = pymysql.connect(host="localhost", user="root", passwd="Clutch123!", database="mysql_database")
    c = conn.cursor()
    criteria = session.get('criteria')
    if criteria:
        if criteria == 'price_high':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY resale_price DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'price_low':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY resale_price;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'remaining_lease_high':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY remaining_lease DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'remaining_lease_low':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY remaining_lease;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'storey_high':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY storey_range DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'storey_low':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY storey_range;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'price_per_sqm_high':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY price_per_sqm DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'price_per_sqm_low':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY price_per_sqm;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        
        elif criteria == 'favourites_high':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY numOfFavourites DESC;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'favourites_low':
            myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY numOfFavourites;")
            c.execute(myquery)
            data = list(c.fetchall())
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

    else:
        myquery = (
            "SELECT id, address, resale_price,flat_type, storey_range FROM Flat;")
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
                list_x.append(len(Flat.query.get(flat_id).favourites))
                tuple_x = tuple(list_x)
                data[x] = tuple_x
            #print(data)

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})


# Route for Searching flats
@views.route('/search/<address>', methods=['GET', 'POST'])
def search(address):
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
            #minPrice = int(price[0])
            #maxPrice = minPrice + 100000
            data = []
            price_range = [word for line in price for word in line.split('-')]
            print(price_range)
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i%2 == 0:
                    data = itertools.chain(Flat.query.filter(Flat.resale_price.between(price_range[i], price_range[i+1])).all())
                    #print(searchedFlats)
            #print(data[0])                
            #return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return render_template("search.html", user=current_user, flats=data[:INDEX])
            
            else:
                return render_template("search.html", user=current_user, flats=data[:INDEX])

        else:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                return render_template("search.html", user=current_user, flats=searchedFlats[:INDEX])

    return render_template('search.html', user=current_user, address=address)

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
    print(address)
    print(towns)
    print(flat_types)
    print(amenities)
    if address:
        address = "%{}%".format(address)

    if price:
        #minPrice = int(price[0])
        #maxPrice = minPrice + 100000 
        price_range = [word for line in price for word in line.split('-')]
        print(price_range)
        for i in range(len(price_range)):
            price_range[i] = int(price_range[i])
            if i%2 == 0:
                data_price = itertools.chain(Flat.query.filter(Flat.resale_price.between(price_range[i], price_range[i+1])).all())
                #print(searchedFlats)
        #print(data_price[0])                
        #return render_template("search.html", user=current_user, flats=data_price[:INDEX])
             
        if address and flat_types and amenities and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address and towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address and towns and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif address:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif towns and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            

        elif towns and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif towns:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif flat_types:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
        
        elif amenities:
            searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
            data_price = [flat for flat in data_price if flat in searchedFlats]
            
            

    else:
        if address and flat_types and amenities and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
        
        elif address and towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
            
        
        elif address and towns and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
            
        
        elif address and towns:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
            
        
        elif address and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            
        
        elif address and flat_types:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
            
        
        elif address and amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
            
        
        elif address:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
            
        
        elif towns and flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            
        
        elif towns and flat_types:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
            

        elif towns and amenities:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
            
        
        elif towns:
            searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
            
        
        elif flat_types and amenities:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
            
        
        elif flat_types:
            searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
            
        
        elif amenities:
            searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
            
    if data_price:
        for flat in data_price:
            data.append(tuple([flat.id, flat.address,
                    flat.resale_price, flat.flat_type, flat.storey_range]))
    else:
        for flat in searchedFlats:
            data.append(tuple([flat.id, flat.address,
                        flat.resale_price, flat.flat_type, flat.storey_range]))
    # print(data[0][0])
    if request.args:
        index = int(request.args.get('index'))
        limit = int(request.args.get('limit'))

        return jsonify({'data': data[index:limit + index]})
    else:
        return jsonify({'data': data})


# Route for Sorting
@views.route('/sort/<criteria>', methods=['GET', 'POST'])
def sort(criteria):
    # If user searches from sort page
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
            #minPrice = int(price[0])
            #maxPrice = minPrice + 100000
            price_range = [word for line in price for word in line.split('-')]
            print(price_range)
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i%2 == 0:
                    data = itertools.chain(Flat.query.filter(Flat.resale_price.between(price_range[i], price_range[i+1])).all())
                    #print(searchedFlats)
            #print(data[0])                
            #return render_template("search.html", user=current_user, flats=data[:INDEX])
         
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
            
            return sorting_criteria(criteria, data)

        elif not price:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()

            return sorting_criteria(criteria, searchedFlats)

    # User did not search or filter from sort page, hence we will use the session information to sort
    else:
        price = session.get('price')
        address = session.get('address')
        towns = session.get('towns')
        flat_types = session.get('flat_types')
        amenities = session.get('amenities')
        print(address)
        print(towns)
        print(flat_types)
        print(amenities)

        if address:
            address = "%{}%".format(address)

        if price:
            #minPrice = int(price[0])
            #maxPrice = minPrice + 100000
            
            price_range = [word for line in price for word in line.split('-')]
            print(price_range)
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i%2 == 0:
                    data = itertools.chain(Flat.query.filter(Flat.resale_price.between(price_range[i], price_range[i+1])).all())
                    #print(searchedFlats)
            #print(data[0])                
            #return render_template("search.html", user=current_user, flats=data[:INDEX])

            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                return sorting_criteria(criteria, data)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
            
            return sorting_criteria(criteria, data)

        elif not price:
            print(criteria)
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria(criteria, searchedFlats)

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                return sorting_criteria(criteria, searchedFlats)
            
            elif not address and not towns and not flat_types and not amenities:
                # no sort or filter or search
                cwd = Path(__file__).parent.absolute()
                os.chdir(cwd)
                conn = sqlite3.connect("database.db")
                #conn = pymysql.connect(host="localhost", user="root", passwd="Clutch123!", database="mysql_database")
                c = conn.cursor()
                print(criteria)

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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
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
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
                elif criteria == 'favourites_high':
                    myquery = (
                    "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY numOfFavourites DESC;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
                elif criteria == 'favourites_low':
                    myquery = (
                    "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY numOfFavourites;")
                    c.execute(myquery)
                    data = list(c.fetchall())
                    session['criteria'] = criteria
                    list_x = []
                    for x in range(INDEX):
                        flat_id = data[x][0]
                        list_x.append(flat_id)
                    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in list_x])
        
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
            #minPrice = int(price[0])
            #maxPrice = minPrice + 100000
            data = []
            price_range = [word for line in price for word in line.split('-')]
            print(price_range)
            for i in range(len(price_range)):
                price_range[i] = int(price_range[i])
                if i%2 == 0:
                    data.extend(Flat.query.filter(Flat.resale_price.between(price_range[i], price_range[i+1])).all())
                    #print(searchedFlats)
            #print(data[0])                
            #return render_template("search.html", user=current_user, flats=data[:INDEX])
            if flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
            
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                data = [flat for flat in data if flat in searchedFlats]
                
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
                data = [flat for flat in data if flat in searchedFlats]
            
            return sorting_criteria_load(criteria, data)

    else:
            if address and flat_types and amenities and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities), Flat.town.in_(towns)).all()
                
            
            elif address and towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns)).all()
                
            
            elif address and towns and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                
            
            elif address and towns:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.town.in_(towns)).all()
                
            
            elif address and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                
            
            elif address and flat_types:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types)).all()
                
            
            elif address and amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address), Flat.amenities.in_(amenities)).all()
                
            
            elif address:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).all()
                
            
            elif towns and flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                
            
            elif towns and flat_types:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.flat_type.in_(flat_types)).all()
                

            elif towns and amenities:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns), Flat.amenities.in_(amenities)).all()
                
            
            elif towns:
                searchedFlats = Flat.query.filter(Flat.town.in_(towns)).all()
                
            
            elif flat_types and amenities:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.amenities.in_(amenities)).all()
                
            
            elif flat_types:
                searchedFlats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
                
            
            elif amenities:
                searchedFlats = Flat.query.filter(Flat.amenities.in_(amenities)).all()
            
            return sorting_criteria_load(criteria, searchedFlats)   


@views.route('/filter', methods=['GET', 'POST'])
def filter():
    if request.method == 'POST':
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        #flat = Flat.query.filter(Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
        if towns:
            if flat_types:
                if amenities:
                    flat = Flat.query.filter(Flat.town.in_(towns)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                else:
                    flat = Flat.query.filter(Flat.town.in_(towns)).filter(
                        Flat.flat_type.in_(flat_types)).all()
            else:
                if amenities:
                    flat = Flat.query.filter(Flat.town.in_(towns)).filter(
                        Flat.amenity.in_(amenities)).all()
                else:
                    flat = Flat.query.filter(Flat.town.in_(towns)).all()
        elif flat_types:
            if amenities:
                flat = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                    Flat.amenity.in_(amenities)).all()
            else:
                flat = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
        elif amenities:
            flat = Flat.query.filter(Flat.amenity.in_(amenities)).all()

        # print(flat)
        return render_template('filter.html', user=current_user, flats=flat[:INDEX])
        # return render_template('sort.html', user=current_user, flats=flat)

    return render_template('filter.html', user=current_user)

## TESTING
## getting image (in flat details only)
def view_image(flatId):
    import requests
    import json

    #find the name of the flat to find the place id
    flat = Flat.query.filter_by(id=flatId).first_or_404()
    flat = Flat.query.get(flatId)
    blk = flat.block
    street = flat.street_name

    name = blk + street

    while(name.find(' ') != -1):
        name = name.replace(' ', '%20')

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + name + "&inputtype=textquery&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload).json()
    primary = response['candidates'][0]
    id = primary['place_id']

    #finding photo reference
    url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + id +"&fields=photos&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload).json()
    res = response['result']
    photoRef = []
    cur = 0
    if 'photos' not in res:
        while (cur < 3):
            photoRef.append(0)
    photos = res['photos']
    noOfPhotos = len(photos) #max number of photo references is 10
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
    #by right should return an array of photo references only, and use these references to get the photo
