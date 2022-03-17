# For creation of stuff that can be viewed on homepage
from db import open_connection
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

views = Blueprint('views', __name__)


@views.route('/reviews', methods=['GET', 'POST'])
@login_required
def review(flat_id):
    if request.method == 'POST':
        review = request.form.get('review')

        if len(review) < 1:
            flash('Review is too short!', category='error')
        elif len(review) > 500:
            flash(
                'Review is too long! Maximum length for a review is 500 characters', category='error')
        else:
            new_review = Review(
                data=review, user_id=current_user.id, flat_id=flat_id)
            db.session.add(new_review)
            db.session.commit()
            flash('Review added!', category='success')

    return render_template("review.html", user=current_user)


@views.route('/delete-review', methods=['GET', 'POST'])
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
    #conn = sqlite3.connect("database.db")
    conn = open_connection()
    # conn = pymysql.connect(host="localhost", user="root", passwd="Clutch123!", database="mysql_database")
    c = conn.cursor()
    myquery = ('SELECT id, address, resale_price,flat_type, storey_range FROM flat;')
    c.execute(myquery)
    data = list(c.fetchall())
    print(data)
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
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                else:
                    if amenities:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

            elif flat_types:
                if amenities:
                    searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                else:
                    searchedFlats = Flat.query.filter(Flat.address.like(
                        address)).filter(Flat.flat_type.in_(flat_types)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:15])

            elif amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:15])

            else:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:15])

        else:
            flash(
                'No results found! Please ensure you typed in the correct format of address.', category='error')
            return render_template("search.html", user=current_user, address=address)

    session.clear()
    return render_template('home.html', user=current_user, flats=data[:15])

# Infinte Scrolling for Home Page


@views.route('/load_home', methods=['GET', 'POST'])
def load_home():
    #os.chdir(os.getcwd() + "/website")
    #print(os.getcwd())
    #conn = sqlite3.connect("database.db")
    conn = open_connection()
    # conn = pymysql.connect(host="localhost", user="root", passwd="Clutch123!", database="mysql_database")
    c = conn.cursor()
    myquery = (
        "SELECT id, address, resale_price,flat_type, storey_range FROM flat;")
    c.execute(myquery)
    data = list(c.fetchall())
    # random.shuffle(data)

    if request.args:
        index = int(request.args.get('index'))
        limit = int(request.args.get('limit'))

        return jsonify({'data': data[index:limit + index]})
    else:
        return jsonify({'data': data})

# Route for Searching flats


@views.route('/search/<search>', methods=['GET', 'POST'])
def search(search):
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
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                else:
                    if amenities:
                        searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                    else:
                        searchedFlats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        return render_template('search.html', user=current_user, flats=searchedFlats[:15])

            elif flat_types:
                if amenities:
                    searchedFlats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:15])

                else:
                    searchedFlats = Flat.query.filter(Flat.address.like(
                        address)).filter(Flat.flat_type.in_(flat_types)).all()
                    return render_template('search.html', user=current_user, flats=searchedFlats[:15])

            elif amenities:
                searchedFlats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:15])

            else:
                searchedFlats = Flat.query.filter(
                    Flat.address.like(address)).all()
                return render_template('search.html', user=current_user, flats=searchedFlats[:15])
        else:
            flash(
                'No results found! Please ensure you typed in the correct format of address.', category='error')
            return render_template("search.html", user=current_user, address=search)

    return render_template('home.html', user=current_user, search=search)

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
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        ## address and towns and flat_types
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats = Flat.query.order_by(
                                Flat.remaining_lease.asc()).all()
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                else:
                    if amenities:
                        ## address and towns and amenities
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats = Flat.query.order_by(
                                Flat.remaining_lease.asc()).all()
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        ## address and towns
                        flats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats = Flat.query.order_by(
                                Flat.remaining_lease.asc()).all()
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
            elif flat_types:
                if amenities:
                    ## address and flat_types and amenities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats = Flat.query.order_by(
                            Flat.remaining_lease.asc()).all()
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                else:
                    ## address and flat_types
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats = Flat.query.order_by(
                            Flat.remaining_lease.asc()).all()
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])

            elif amenities:
                ## address and amenities
                flats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_low':
                    flats = Flat.query.order_by(
                        Flat.remaining_lease.asc()).all()
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_high':
                    flats.sort(
                        key=lambda x: x.price_per_sqm, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_low':
                    flats.sort(
                        key=lambda x: x.price_per_sqm, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
            else:
                # address
                flats = Flat.query.filter(
                    Flat.address.like(address)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_low':
                    flats = Flat.query.order_by(
                        Flat.remaining_lease.asc()).all()
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_high':
                    flats.sort(
                        key=lambda x: x.price_per_sqm, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_low':
                    flats.sort(
                        key=lambda x: x.price_per_sqm, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])

        elif towns or flat_types or amenities:
            if towns:
                if flat_types:
                    if amenities:
                        ## town and flat_types and amenities
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats = Flat.query.order_by(
                                Flat.remaining_lease.asc()).all()
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        ## town and flat_types
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats = Flat.query.order_by(
                                Flat.remaining_lease.asc()).all()
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
            elif flat_types:
                if amenities:
                    ## flat_types and amenities
                    flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                        Flat.amenity.in_(amenities)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats = Flat.query.order_by(
                            Flat.remaining_lease.asc()).all()
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                else:
                    # flat_types
                    flats = Flat.query.filter(
                        Flat.flat_type.in_(flat_types)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats = Flat.query.order_by(
                            Flat.remaining_lease.asc()).all()
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
            else:
                # amenities
                flats = Flat.query.filter(Flat.amenity.in_(amenities)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_low':
                    flats = Flat.query.order_by(
                        Flat.remaining_lease.asc()).all()
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_high':
                    flats.sort(
                        key=lambda x: x.price_per_sqm, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_low':
                    flats.sort(
                        key=lambda x: x.price_per_sqm, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
        else:
            # nothing searched or sorted or filtered
            if criteria == 'price_high':
                flats = Flat.query.order_by(Flat.resale_price.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'price_low':
                flats = Flat.query.order_by(Flat.resale_price.asc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'remaining_lease_high':
                flats = Flat.query.order_by(Flat.remaining_lease.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'remaining_lease_low':
                flats = Flat.query.order_by(Flat.remaining_lease.asc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'price_per_sqm_high':
                flats.sort(
                    key=lambda x: x.price_per_sqm, reverse=True)
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'price_per_sqm_low':
                flats.sort(
                    key=lambda x: x.price_per_sqm, reverse=False)
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])

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
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        ## address, towns, flat_types
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                else:
                    if amenities:
                        ## address, towns, amenities
                        flats = Flat.query.filter(Flat.address.like(address)).filter(
                            Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        ## address, towns
                        flats = Flat.query.filter(Flat.address.like(
                            address)).filter(Flat.town.in_(towns)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
            elif flat_types:
                if amenities:
                    ## address, flat_types, amenities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                else:
                    ## address, flat_types
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.flat_type.in_(flat_types)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])

            elif amenities:
                ## address, amenities
                flats = Flat.query.filter(Flat.address.like(
                    address)).filter(Flat.amenity.in_(amenities)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_low':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_high':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_low':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
            else:
                # address
                flats = Flat.query.filter(
                    Flat.address.like(address)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_low':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_high':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_low':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])

        elif towns or flat_types or amenities:
            if towns:
                if flat_types:
                    if amenities:
                        ## town, flat_types, amenities
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        ## town, flat_types
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.flat_type.in_(flat_types)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                else:
                    if amenities:
                        ## town, amenities
                        flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                            Flat.amenity.in_(amenities)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                    else:
                        # town
                        flats = Flat.query.filter(Flat.town.in_(towns)).all()
                        if criteria == 'price_high':
                            flats.sort(
                                key=lambda x: x.resale_price, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_low':
                            flats.sort(key=lambda x: x.resale_price,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_high':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'remaining_lease_low':
                            flats.sort(
                                key=lambda x: x.remaining_lease, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_high':
                            flats.sort(
                                key=lambda x: x.storey_range, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'storey_low':
                            flats.sort(key=lambda x: x.storey_range,
                                       reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_high':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=True)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
                        elif criteria == 'price_per_sqm_low':
                            flats.sort(
                                key=lambda x: x.price_per_sqm, reverse=False)
                            session['criteria'] = criteria
                            return render_template('sort.html', user=current_user, flats=flats[:15])
            elif flat_types:
                if amenities:
                    ## flat_types, amenities
                    flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                        Flat.amenity.in_(amenities)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                
                else:
                    # flat_types
                    flats = Flat.query.filter(
                        Flat.flat_type.in_(flat_types)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=True)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(
                            key=lambda x: x.price_per_sqm, reverse=False)
                        session['criteria'] = criteria
                        return render_template('sort.html', user=current_user, flats=flats[:15])
            else:
                # amenities
                flats = Flat.query.filter(Flat.amenity.in_(amenities)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'remaining_lease_low':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_high':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
                elif criteria == 'price_per_sqm_low':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                    session['criteria'] = criteria
                    return render_template('sort.html', user=current_user, flats=flats[:15])
        
        else:
            # no sort or filter or search
            if criteria == 'price_high':
                flats = Flat.query.order_by(Flat.resale_price.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'price_low':
                flats = Flat.query.order_by(Flat.resale_price.asc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'remaining_lease_high':
                flats = Flat.query.order_by(Flat.remaining_lease.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'remaining_lease_low':
                flats = Flat.query.order_by(Flat.remaining_lease.asc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'storey_high':
                flats = Flat.query.order_by(Flat.storey_range.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'storey_low':
                flats = Flat.query.order_by(Flat.storey_range.asc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'price_per_sqm_high':
                flats = Flat.query.order_by(Flat.price_per_sqm.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])
            elif criteria == 'price_per_sqm_low':
                flats = Flat.query.order_by(Flat.price_per_sqm.asc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:15])

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
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                            # print(data[0][0])
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                else:
                    ## address, towns, flat_types
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.town.in_(towns)).filter(Flat.flat_type.in_(flat_types)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                            # print(data[0][0])
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

            else:
                if amenities:
                    ## address, towns, amentities
                    flats = Flat.query.filter(Flat.address.like(address)).filter(
                        Flat.town.in_(towns)).filter(Flat.amenity.in_(amenities)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                            # print(data[0][0])
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    elif criteria == 'remaining_lease_low':
                        flats.sort(key=lambda x: x.remaining_lease,
                                   reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    elif criteria == 'storey_high':
                        flats.sort(key=lambda x: x.storey_range, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'storey_low':
                        flats.sort(key=lambda x: x.storey_range, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    
                    elif criteria == 'price_per_sqm_high':
                        flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})
                    
                    elif criteria == 'price_per_sqm_low':
                        flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                else:
                    ## address, towns
                    flats = Flat.query.filter(Flat.address.like(
                        address)).filter(Flat.town.in_(towns)).all()
                    if criteria == 'price_high':
                        flats.sort(key=lambda x: x.resale_price, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                            # print(data[0][0])
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'price_low':
                        flats.sort(key=lambda x: x.resale_price, reverse=False)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

                    elif criteria == 'remaining_lease_high':
                        flats.sort(
                            key=lambda x: x.remaining_lease, reverse=True)
                        for flat in flats:
                            data.append(tuple(
                                [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        if request.args:
                            index = int(request.args.get('index'))
                            limit = int(request.args.get('limit'))

                            return jsonify({'data': data[index:limit + index]})
                        else:
                            return jsonify({'data': data})

        elif flat_types:
            if amenities:
                ## address, flat_types, amenities
                flats = Flat.query.filter(Flat.address.like(address)).filter(
                    Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        # print(data[0][0])
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                elif criteria == 'remaining_lease_low':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                
                elif criteria == 'price_per_sqm_high':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                
                elif criteria == 'price_per_sqm_low':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

            else:
                ## address, flat_types
                flats = Flat.query.filter(Flat.address.like(address)).filter(
                    Flat.flat_type.in_(flat_types)).all()
                if criteria == 'price_high':
                    flats.sort(key=lambda x: x.resale_price, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                        # print(data[0][0])
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

                elif criteria == 'price_low':
                    flats.sort(key=lambda x: x.resale_price, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

                elif criteria == 'remaining_lease_high':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                elif criteria == 'remaining_lease_low':
                    flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                elif criteria == 'storey_high':
                    flats.sort(key=lambda x: x.storey_range, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

                elif criteria == 'storey_low':
                    flats.sort(key=lambda x: x.storey_range, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                
                elif criteria == 'price_per_sqm_high':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})
                
                elif criteria == 'price_per_sqm_low':
                    flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                    for flat in flats:
                        data.append(tuple(
                            [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    if request.args:
                        index = int(request.args.get('index'))
                        limit = int(request.args.get('limit'))

                        return jsonify({'data': data[index:limit + index]})
                    else:
                        return jsonify({'data': data})

        elif amenities:
            ## address, amenities
            flats = Flat.query.filter(Flat.address.like(
                address)).filter(Flat.amenity.in_(amenities)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})

                else:
                    return jsonify({'data': data})

        else:
            # address
            flats = Flat.query.filter(Flat.address.like(address)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

    elif towns or flat_types or amenities:
        ## towns, flat_types, amenities
        if towns and flat_types and amenities:
            ## town, flat_type, amenity
            flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                Flat.flat_type.in_(flat_types)).filter(Flat.amenity.in_(amenities)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

        ## towns, flat_types
        elif towns and flat_types:
            ## town, flat_type
            flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                Flat.flat_type.in_(flat_types)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

        ## towns and amenities
        elif towns and amenities:
            flats = Flat.query.filter(Flat.town.in_(towns)).filter(
                Flat.amenities.in_(amenities)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
                

        # towns
        elif towns:
            flats = Flat.query.filter(Flat.town.in_(towns)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

        ## flat_types and amenities
        elif flat_types and amenities:
            ## flat_type, amenities
            flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).filter(
                Flat.amenities.in_(amenities)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

        # flat_types
        elif flat_types:
            flats = Flat.query.filter(Flat.flat_type.in_(flat_types)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

        # amenities
        elif amenities:
            flats = Flat.query.filter(Flat.amenity.in_(amenities)).all()
            if criteria == 'price_high':
                flats.sort(key=lambda x: x.resale_price, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                    # print(data[0][0])
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'price_low':
                flats.sort(key=lambda x: x.resale_price, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_high':
                flats.sort(key=lambda x: x.remaining_lease, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})

            elif criteria == 'remaining_lease_low':
                flats.sort(key=lambda x: x.remaining_lease, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'storey_high':
                flats.sort(key=lambda x: x.storey_range, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'storey_low':
                flats.sort(key=lambda x: x.storey_range, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_high':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            
            elif criteria == 'price_per_sqm_low':
                flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
                for flat in flats:
                    data.append(tuple(
                        [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))

                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
            

    # no search or filter
    else:
        if criteria == 'price_high':
            flats = Flat.query.order_by(Flat.resale_price.desc()).all()
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
                # print(data[0][0])
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_low':
            flats = Flat.query.order_by(Flat.resale_price.asc()).all()
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'remaining_lease_high':
            flats = Flat.query.order_by(Flat.remaining_lease.desc()).all()
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'remaining_lease_low':
            flats = Flat.query.order_by(Flat.remaining_lease.asc()).all()
            flats.sort(key=lambda x: x.remaining_lease, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        elif criteria == 'storey_high':
            flats = Flat.query.order_by(Flat.storey_range.desc()).all()
            flats.sort(key=lambda x: x.storey_range, reverse=True)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'storey_low':
            flats = Flat.query.order_by(Flat.storey_range.asc()).all()
            flats.sort(key=lambda x: x.storey_range, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_per_sqm_high':
            flats = Flat.query.order_by(Flat.price_per_sqm.desc()).all()
            flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
        
        elif criteria == 'price_per_sqm_low':
            flats = Flat.query.order_by(Flat.price_per_sqm.asc()).all()
            flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))

                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        return jsonify({})
    


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
        return render_template('filter.html', user=current_user, flats=flat[:15])
        # return render_template('sort.html', user=current_user, flats=flat)

    return render_template('filter.html', user=current_user)
