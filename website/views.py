# For creation of stuff that can be viewed on homepage
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
@login_required
def flat_details(flatId):
    flat = Flat.query.filter_by(id=flatId).first_or_404()
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
    return render_template("flat_details.html", user=current_user, flat=flat)


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
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        address = request.form.get('search')
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        session['amenities'] = amenities
        address = "%{}%".format(address)
        if address:
            if towns:
                if flat_types:
                    if amenities:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(Flat.town.in_(
                            towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                else:
                    if amenities:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

            elif flat_types:
                if amenities:
                    searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                else:
                    searchedFlats = Flat.query.filter(Flat.address.like(
                        address)).filter(Flat.flat_type.in_(flat_types)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

            elif amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

            else:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

        else:
            flash(
                'No results found! Please ensure you typed in the correct format of address.', category='error')
            return render_template("search.html", user=current_user, address=address)
    session.clear()
    return render_template('home.html', user=current_user, flats=[Flat.query.get(x) for x in range(INDEX)], favourites = current_user.favourites)



@views.route('/unfavourite', methods=['POST'])
@login_required
def unfavourite():
    favourite = json.loads(request.data)
    flatID = favourite['favouriteID']
    flat = Flat.query.get(flatID)
    for favourite in current_user.favourites:
        if favourite.flat_id == flatID:
            db.session.delete(favourite)
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
    db.session.commit()
    return jsonify({"favourite_count": len(flat.favourites)})

@views.route('/favourite_count', methods=['POST'])
def favourite_count():
    flat = json.loads(request.data)
    flatID = flat['flatID']
    flat = Flat.query.get(flatID)
    return jsonify({"favourite_count": len(flat.favourites)})

    
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
            print(data)

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})


# Route for Searching flats
@views.route('/search/<address>', methods=['GET', 'POST'])
def search(address):
    if request.method == 'POST':
        address = request.form.get('search')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        session['address'] = address
        session['towns'] = towns
        session['flat_types'] = flat_types
        session['amenities'] = amenities
        address = "%{}%".format(address)

        if address:
            if towns:
                if flat_types:
                    if amenities:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(Flat.town.in_(
                            towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                else:
                    if amenities:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

            elif flat_types:
                if amenities:
                    searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

                else:
                    searchedFlats = Flat.query.filter(Flat.address.like(
                        address)).filter(Flat.flat_type.in_(flat_types)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

            elif amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])

            else:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:INDEX])
        else:
            flash(
                'No results found! Please ensure you typed in the correct format of address.', category='error')
            return render_template("search.html", user=current_user, address=address)

    return render_template('search.html', user=current_user, address=address)

# Infinite Scrolling for Search Page


@views.route('/load_search', methods=['GET', 'POST'])
def load_search():
    data = []
    address = session.get('address')
    towns = session.get('towns')
    flat_types = session.get('flat_types')
    amenities = session.get('amenities')
    print(address)
    print(towns)
    print(flat_types)
    print(amenities)
    address = "%{}%".format(address)
    if towns:
        if flat_types:
            if amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(Flat.town.in_(
                    towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()

            else:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                    Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()

        else:
            if amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                    Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()

            else:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.town.in_(towns)).all()

    elif flat_types:
        if amenities:
            searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()

        else:
            searchedFlats = Flat.query.filter(Flat.address.like(
                address)).filter(Flat.flat_type.in_(flat_types)).all()

    elif amenities:
        searchedFlats = Flat.query.filter(Flat.address.like(
            address)).filter(Flat.amenity.in_(amenities)).all()

    else:
        searchedFlats = Flat.query.filter(
            Flat.address.like(address)).all()

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
    if request.method == 'POST':
        address = request.form.get('search')
        towns = request.form.getlist('town')
        flat_types = request.form.getlist('flat_type')
        amenities = request.form.getlist('amenity')
        if address:
            address = "%{}%".format(address)
            if towns:
                if flat_types:
                    if amenities:
                        ## address and towns and flat_types and amenities
                        flats = Flat.query.filter(Flat.address.like(address)).filter(Flat.town.in_(
                            towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        ## address and towns and flat_types
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        return sorting_criteria(criteria, flats)
                else:
                    if amenities:
                        ## address and towns and amenities
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        ## address and towns
                        flats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        return sorting_criteria(criteria, flats)
            elif flat_types:
                if amenities:
                    ## address and flat_types and amenities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return sorting_criteria(criteria, flats)
                else:
                    ## address and flat_types
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).all()
                    return sorting_criteria(criteria, flats)

            elif amenities:
                ## address and amenities
                flats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                return sorting_criteria(criteria, flats)
            else:
                # address
                flats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return sorting_criteria(criteria, flats)

        elif towns or flat_types or amenities:
            if towns:
                if flat_types:
                    if amenities:
                        ## town and flat_types and amenities
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        ## town and flat_types
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).all()
                        return sorting_criteria(criteria, flats)
            elif flat_types:
                if amenities:
                    ## flat_types and amenities
                    flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                        Flat.amenity.in_(amenities)).all()
                    return sorting_criteria(criteria, flats)
                else:
                    # flat_types
                    flats = Flat.query.filter(
                        Flat.flat_type.in_(flat_types)).all()
                    return sorting_criteria(criteria, flats)
            else:
                # amenities
                flats = Flat.query.filter(Flat.amenity.in_(amenities)).all()
                return sorting_criteria(criteria, flats)
        #else:
            # nothing searched or sorted or filtered
            #return sorting_criteria(criteria, flats)

    # User did not search or filter from sort page, hence we will use the session information to sort
    else:
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
            if towns:
                if flat_types:
                    if amenities:
                        ## address, towns, flat_types, amenities
                        flats = Flat.query.filter(Flat.address.like(address)).filter(Flat.town.in_(
                            towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        ## address, towns, flat_types
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        return sorting_criteria(criteria, flats)
                else:
                    if amenities:
                        ## address, towns, amenities
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        ## address, towns
                        flats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        return sorting_criteria(criteria, flats)
            elif flat_types:
                if amenities:
                    ## address, flat_types, amenities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return sorting_criteria(criteria, flats)
                else:
                    ## address, flat_types
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).all()
                    return sorting_criteria(criteria, flats)

            elif amenities:
                ## address, amenities
                flats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                return sorting_criteria(criteria, flats)
            else:
                # address
                flats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return sorting_criteria(criteria, flats)

        elif towns or flat_types or amenities:
            if towns:
                if flat_types:
                    if amenities:
                        ## town, flat_types, amenities
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        ## town, flat_types
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).all()
                        return sorting_criteria(criteria, flats)
                else:
                    if amenities:
                        ## town, amenities
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.amenity.in_(amenities)).all()
                        return sorting_criteria(criteria, flats)
                    else:
                        # town
                        flats = Flat.query.filter(Flat.town.in_(towns)).all()
                        return sorting_criteria(criteria, flats)
            elif flat_types:
                if amenities:
                    ## flat_types, amenities
                    flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                        Flat.amenity.in_(amenities)).all()
                    return sorting_criteria(criteria, flats)
                
                else:
                    # flat_types
                    flats = Flat.query.filter(
                        Flat.flat_type.in_(flat_types)).all()
                    #print(flats)
                    return sorting_criteria(criteria, flats)
                    
            else:
                # amenities
                flats = Flat.query.filter(Flat.amenity.in_(amenities)).all()
                return sorting_criteria(criteria, flats)
        else:
            # no sort or filter or search
            cwd = Path(__file__).parent.absolute()
            os.chdir(cwd)
            conn = sqlite3.connect("database.db")
            #conn = pymysql.connect(host="localhost", user="root", passwd="Clutch123!", database="mysql_database")
            c = conn.cursor()

            if criteria == 'price_high':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY resale_price DESC;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'price_low':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY resale_price;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'remaining_lease_high':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY remaining_lease DESC;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'remaining_lease_low':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY remaining_lease;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'storey_high':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY storey_range DESC;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'storey_low':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY storey_range;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'price_per_sqm_high':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY price_per_sqm DESC;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            elif criteria == 'price_per_sqm_low':
                myquery = (
                "SELECT id, address, resale_price,flat_type, storey_range FROM Flat ORDER BY price_per_sqm;")
                c.execute(myquery)
                data = list(c.fetchall())
                session['criteria'] = criteria
                return render_template('home.html', user=current_user, flats=data[:INDEX])
            
    return render_template('sort.html', user=current_user)


# Infinite Scrolling for Sort Page
@views.route('/load_sort', methods=['GET', 'POST'])
def load_sort():
    data = []
    criteria = session.get('criteria')
    address = session.get('address')
    flat_types = session.get('flat_types')
    amenities = session.get('amenities')
    towns = session.get('towns')
    if address:
        address = "%{}%".format(address)
        if towns:
            if flat_types:
                if amenities:
                    ## address, towns, flat_types, amenities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(Flat.town.in_(
                        towns)).filter(Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return sorting_criteria_load(criteria, flats)

                else:
                    ## address, towns, flat_types
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                    return sorting_criteria_load(criteria, flats)

            else:
                if amenities:
                    ## address, towns, amentities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                    return sorting_criteria_load(criteria, flats)

                else:
                    ## address, towns
                    flats = Flat.query.filter(Flat.address.like(
                        address)).filter(Flat.town.in_(towns)).all()
                    return sorting_criteria_load(criteria, flats)

        elif flat_types:
            if amenities:
                ## address, flat_types, amenities
                flats = Flat.query.filter(Flat.address.like(address)).filter(
                    Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                return sorting_criteria_load(criteria, flats)

            else:
                ## address, flat_types
                flats = Flat.query.filter(Flat.address.like(address)).filter(
                    Flat.flat_type.in_(flat_types)).all()
                return sorting_criteria_load(criteria, flats)

        elif amenities:
            ## address, amenities
            flats = Flat.query.filter(Flat.address.like(
                address)).filter(Flat.amenity.in_(amenities)).all()
            return sorting_criteria_load(criteria, flats)

        else:
            # address
            flats = Flat.query.filter(Flat.address.like(address)).all()
            return sorting_criteria_load(criteria, flats)

    elif towns or flat_types or amenities:
        ## towns, flat_types, amenities
        if towns and flat_types and amenities:
            ## town, flat_type, amenity
            flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
            return sorting_criteria_load(criteria, flats)

        ## towns, flat_types
        elif towns and flat_types:
            ## town, flat_type
            flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                Flat.flat_type.in_(flat_types)).all()
            return sorting_criteria_load(criteria, flats)

        ## towns and amenities
        elif towns and amenities:
            flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                Flat.amenities.in_(amenities)).all()
            return sorting_criteria_load(criteria, flats)
                

        # towns
        elif towns:
            flats = Flat.query.filter(Flat.town.in_(towns)).all()
            return sorting_criteria_load(criteria, flats)

        ## flat_types and amenities
        elif flat_types and amenities:
            ## flat_type, amenities
            flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                Flat.amenities.in_(amenities)).all()
            return sorting_criteria_load(criteria, flats)

        # flat_types
        elif flat_types:
            flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
            return sorting_criteria_load(criteria, flats)


        # amenities
        elif amenities:
            flats = Flat.query.filter(Flat.amenity.in_(amenities)).all()
            return sorting_criteria_load(criteria, flats)
            

    # no search or filter
    else:
        return sorting_criteria_load(criteria, data)    


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
