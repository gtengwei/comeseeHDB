## For creation of stuff that can be viewed on homepage
from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from .models import *
from . import db
import json
import sqlite3
import os
import random

views = Blueprint('views', __name__)

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

## Route for every flat
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


## Route for Home Page
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    myquery = ("SELECT id, street_name, resale_price,flat_type, storey_range FROM Flat;")
    c.execute(myquery)
    data=list(c.fetchall())
    #random.shuffle(data)
    #print(os.getcwd())
    
    ## Search for flats from homepage
    if request.method == 'POST':
        street_name = request.form.get('search')
        session['street_name'] = street_name
        street_name = "%{}%".format(street_name)
        searchedFlats = Flat.query.filter(Flat.street_name.like(street_name)).all()
        if searchedFlats:
            return render_template('search.html', user=current_user, flats=searchedFlats[:15])
            #return redirect(url_for('views.search'), street_name = street_name)
        else:
            flash('No results found! Please ensure you typed in the correct format of address.', category='error')
            return render_template("search.html", user = current_user, street_name = street_name)

    session.clear()
    return render_template('home.html', user=current_user,flats=data[:15])

## Infinte Scrolling for Home Page
@views.route('/load_home', methods=['GET', 'POST'])
def load_home():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    myquery = ("SELECT id, street_name, resale_price,flat_type, storey_range FROM Flat;")
    c.execute(myquery)
    data=list(c.fetchall())
    #random.shuffle(data)

    if request.args:
        index = int(request.args.get('index'))
        limit = int(request.args.get('limit'))
    
        return jsonify({'data': data[index:limit + index]})
    else:
        return jsonify({'data': data})

## Route for Searching flats
@views.route('/search/<search>', methods=['GET', 'POST'])
def search(search):
    if request.method == 'POST':
        street_name = request.form.get('search')
        session['street_name'] = street_name
        street_name = "%{}%".format(street_name)
        searchedFlats = Flat.query.filter(Flat.street_name.like(street_name)).all()
        #print(searchedFlats[0].street_name)
        if searchedFlats:
            return render_template('search.html', user=current_user, flats=searchedFlats[:15], search = search)
            #return redirect(url_for('views.search'), street_name = street_name)
        else:
            flash('No results found! Please ensure you typed in the correct format of address.', category='error')
            return render_template("search.html", user = current_user, street_name = search)

## Infinite Scrolling for Search Page
@views.route('/load_search', methods=['GET', 'POST'])
def load_search():
    data = []
    street_name = session.get('street_name')
    #print(street_name)
    street_name = "%{}%".format(street_name)
    flats = Flat.query.filter(Flat.street_name.like(street_name)).all()
    for flat in flats:
        data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
    print(data[0][0])
    if request.args:
        index = int(request.args.get('index'))
        limit = int(request.args.get('limit'))
    
        return jsonify({'data': data[index:limit + index]})
    else:
        return jsonify({'data': data})


## Route for Sorting
@views.route('/sort/<criteria>', methods=['GET', 'POST'])
def sort(criteria):
        if request.method == 'POST':
            search(request.form.get('search'))
        street_name = session.get('street_name')
        if street_name:
            street_name = "%{}%".format(street_name)
            flats = Flat.query.filter(Flat.street_name.like(street_name)).all()
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
        else:
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
        

        return render_template('sort.html', user=current_user)
            

## Infinite Scrolling for Sort Page
@views.route('/load_sort', methods=['GET', 'POST'])
def load_sort():
    data = [] 
    criteria = session.get('criteria')
    street_name = session.get('street_name')
    if street_name:
        street_name = "%{}%".format(street_name)
        flats = Flat.query.filter(Flat.street_name.like(street_name)).all()
        if criteria == 'price_high':    
            flats.sort(key=lambda x: x.resale_price, reverse=True)
            for flat in flats:
                data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
                #print(data[0][0])
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
        
                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_low':
            flats.sort(key=lambda x: x.resale_price, reverse=False)
            for flat in flats:
                data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
        
                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'remaining_lease_high':
            flats.sort(key=lambda x: x.remaining_lease, reverse=True)
            for flat in flats:
                data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
    
                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})
    
    else:
        if criteria == 'price_high':    
            flats = Flat.query.order_by(Flat.resale_price.desc()).all()
            for flat in flats:
                data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
                #print(data[0][0])
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
        
                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_low':
            flats = Flat.query.order_by(Flat.resale_price.asc()).all()
            for flat in flats:
                data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
        
                return jsonify({'data': data[index:limit + index]})
            else:
                return jsonify({'data': data})

        elif criteria == 'remaining_lease_high':
            flats = Flat.query.order_by(Flat.remaining_lease.desc()).all()
            for flat in flats:
                data.append(tuple([flat.id, flat.street_name, flat.resale_price, flat.flat_type, flat.storey_range]))
                if request.args:
                    index = int(request.args.get('index'))
                    limit = int(request.args.get('limit'))
        
                    return jsonify({'data': data[index:limit + index]})
                else:
                    return jsonify({'data': data})
        return jsonify({})
        
    