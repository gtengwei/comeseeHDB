## Helper functions for website
## To organise the code
from website import mail
from flask import flash, url_for, render_template, session, jsonify, request
from flask_mail import Message
from flask_login import current_user
from random import randint
from .models import Flat
from . import db
from datetime import datetime
import json
import random

INDEX = 20

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
    msg = Message("Password Reset Request",recipients = [user.email], sender = 'noreply@comeseeHDB.com')

    msg.body = f'''
    To reset your password, visit the following link:
    {url_for('auth.reset_token', token=token, _external=True)}
    This link will expire in 2 minutes.
    If you did not make this request, please ignore this email and no changes will be made.
    '''
    
    mail.send(msg)

def send_mail_verify(user):
    token = user.get_token()
    msg = Message("Verify your email",recipients = [user.email], sender = 'noreply@comeseeHDB.com')

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

def generate_random_flat():
    random_num = randint(1, Flat.query.count())
    #print(random_num)
    return random_num

def sorting_criteria(criteria, flats = []):
    RANDOM = generate_random_flat()
    if criteria == 'price_high':
        flats.sort(key=lambda x: int(x.resale_price), reverse=True)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'price_low':
        flats.sort(key=lambda x: x.resale_price,reverse=False)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'remaining_lease_high':
        flats.sort(key=lambda x: x.remaining_lease, reverse=True)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'remaining_lease_low':
        flats.sort(key=lambda x: x.remaining_lease, reverse=False)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'storey_high':
        flats.sort(key=lambda x: x.storey_range, reverse=True)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'storey_low':
        flats.sort(key=lambda x: x.storey_range, reverse=False)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'price_per_sqm_high':
        flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'price_per_sqm_low':
        flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)
    
    elif criteria == 'favourites_high':
        flats.sort(key=lambda x: x.numOfFavourites, reverse=True)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif criteria == 'favourites_low':
        flats.sort(key=lambda x: x.numOfFavourites, reverse=False)
        session['criteria'] = criteria
        return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

    elif flats == []:
        if criteria == 'price_high':
                flats = Flat.query.order_by(Flat.resale_price.desc()).all()
                session['criteria'] = criteria
                return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'price_low':
            flats = Flat.query.order_by(Flat.resale_price.asc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'remaining_lease_high':
            flats = Flat.query.order_by(Flat.remaining_lease.desc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'remaining_lease_low':
            flats = Flat.query.order_by(Flat.remaining_lease.asc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'storey_high':
            flats = Flat.query.order_by(Flat.storey_range.desc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'storey_low':
            flats = Flat.query.order_by(Flat.storey_range.asc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'price_per_sqm_high':
            flats = Flat.query.order_by(Flat.price_per_sqm.desc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)

        elif criteria == 'price_per_sqm_low':
            flats = Flat.query.order_by(Flat.price_per_sqm.asc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)
        
        elif criteria == 'favourites_high':
            flats = Flat.query.order_by(Flat.numOfFavourites.desc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)
        
        elif criteria == 'favourites_low':
            flats = Flat.query.order_by(Flat.numOfFavourites.asc()).all()
            session['criteria'] = criteria
            return render_template('sort.html', user=current_user, flats=flats[:INDEX], data_length = len(flats), random = RANDOM)
    
    return render_template('sort.html', user=current_user, flats=flats[:INDEX], random = RANDOM)
    



def sorting_criteria_load(criteria, flats = []):
    data = []
    if criteria == 'price_high':
        flats.sort(key=lambda x: x.resale_price, reverse=True)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            # print(data[0][0])
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})

    elif criteria == 'price_low':
        flats.sort(key=lambda x: x.resale_price, reverse=False)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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
            return jsonify({'data': data})
        else:
            return jsonify({'data': data})

    elif criteria == 'remaining_lease_high':
        flats.sort(
            key=lambda x: x.remaining_lease, reverse=True)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})
    elif criteria == 'remaining_lease_low':
        flats.sort(key=lambda x: x.remaining_lease,
                    reverse=False)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})
    elif criteria == 'storey_high':
        flats.sort(key=lambda x: x.storey_range, reverse=True)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})

    elif criteria == 'storey_low':
        flats.sort(key=lambda x: x.storey_range, reverse=False)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})
    
    elif criteria == 'price_per_sqm_high':
        flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})
    
    elif criteria == 'price_per_sqm_low':
        flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})
    
    elif criteria == 'favourites_high':
        flats.sort(key=lambda x: x.numOfFavourites, reverse=True)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})
    
    elif criteria == 'favourites_low':
        flats.sort(key=lambda x: x.numOfFavourites, reverse=False)
        for flat in flats:
            data.append(tuple(
                [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
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

            return jsonify({'data': data})
        else:
            return jsonify({'data': data})

    
    elif flats == []:
        if criteria == 'price_high':
            flats = Flat.query.order_by(Flat.resale_price.desc()).all()
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
                # print(data[0][0])
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

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_low':
            flats = Flat.query.order_by(Flat.resale_price.asc()).all()
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'remaining_lease_high':
            flats = Flat.query.order_by(Flat.remaining_lease.desc()).all()
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'remaining_lease_low':
            flats = Flat.query.order_by(Flat.remaining_lease.asc()).all()
            flats.sort(key=lambda x: x.remaining_lease, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        elif criteria == 'storey_high':
            flats = Flat.query.order_by(Flat.storey_range.desc()).all()
            flats.sort(key=lambda x: x.storey_range, reverse=True)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'storey_low':
            flats = Flat.query.order_by(Flat.storey_range.asc()).all()
            flats.sort(key=lambda x: x.storey_range, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

        elif criteria == 'price_per_sqm_high':
            flats = Flat.query.order_by(Flat.price_per_sqm.desc()).all()
            flats.sort(key=lambda x: x.price_per_sqm, reverse=True)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        
        elif criteria == 'price_per_sqm_low':
            flats = Flat.query.order_by(Flat.price_per_sqm.asc()).all()
            flats.sort(key=lambda x: x.price_per_sqm, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
            
        elif criteria == 'favourites_high':
            flats = Flat.query.order_by(Flat.numOfFavourites.desc()).all()
            flats.sort(key=lambda x: x.numOfFavourites, reverse=True)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})
        
        elif criteria == 'favourites_low':
            flats = Flat.query.order_by(Flat.numOfFavourites.asc()).all()
            flats.sort(key=lambda x: x.numOfFavourites, reverse=False)
            for flat in flats:
                data.append(tuple(
                    [flat.id, flat.address_no_postal_code, flat.resale_price, flat.flat_type, flat.storey_range, flat.image]))
            if request.args:
                index = int(request.args.get('index'))
                limit = int(request.args.get('limit'))
                for x in range(len(data)):
                    tuple_x = data[x]
                    list_x = list(tuple_x)
                    flat_id = list_x[0]
                    list_x.append(len(Flat.query.get(flat_id).favourites))
                    tuple_x = tuple(list_x)
                    data[x] = tuple_x

                return jsonify({'data': data})
            else:
                return jsonify({'data': data})

    return jsonify({})
    
    