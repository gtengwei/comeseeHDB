## Everything related to the user
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, current_app, send_from_directory
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_required, current_user
from datetime import datetime
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
            print(request)
            username = request.form.get('username')
            check_username = User.query.filter_by(username=username).first()
            if username == current_user.username:
                flash('Username must be different from current username.', category='error')
            elif check_username:
                flash('Username already exists.', category='error')
            elif len(username) < 4:
                flash('Username must be at least 4 character long.', category='error')
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
               
                elif postal_code == user.postal_code:
                    flash('Postal code must be different from current postal code.', category='error')

                else:
                    user.postal_code = postal_code
                    user.postal_code_change = datetime.now()
                    db.session.commit()
                    flash('Postal Code changed successfully!', category='success')
                    return redirect(url_for('user.profile', username=username))
            else:
                flash('Incorrect password, try again.', category='error')

    return render_template("change_postal_code.html", user=current_user)

## Display like flats for every unique user
## To be completed
@user.route('/flat_likes/<username>', methods=['GET', 'POST']) 
@login_required
def flat_likes(username):
    like_list = []
    for x in current_user.likes:
            like_list.append(x.flat_id)
    if request.method == 'POST':
        address = request.form.get('searchFlatLikes')
        print(address)
        address = "%{}%".format(address)
        flats = Flat.query.join(FlatLikes, FlatLikes.flat_id == Flat.id)\
        .filter(FlatLikes.user_id == current_user.id)\
        .filter(Flat.address.like(address)).all()
        if flats:
            return render_template("flat_likes.html", user=current_user, flats=flats)
        else:
            flash('No results found.', category='error')
            return render_template("flat_likes.html", user=current_user, flats=[])
            
    return render_template("flat_likes.html", user=current_user, flats = [Flat.query.get(x) for x in like_list])

@user.route('/property_likes/<username>', methods=['GET', 'POST'])
def property_likes(username):
    like_list = []
    for x in current_user.propertyLikes:
            like_list.append(x.prop_id)
    if request.method == 'POST':
        address = request.form.get('searchPropertyLikes')
        print(address)
        address = "%{}%".format(address)
        properties = Property.query.join(PropertyLikes, PropertyLikes.prop_id == Property.id)\
        .filter(PropertyLikes.user_id == current_user.id)\
        .filter(Property.address_no_postal_code.like(address)).all()
        if properties:
            return render_template("property_likes.html", user=current_user, properties=properties)
        else:
            flash('No results found.', category='error')
            return render_template("property_likes.html", user=current_user, properties=[])
    print(like_list)
    return render_template("property_likes.html", user=current_user, properties = [Property.query.get(x) for x in like_list])

#Allow AGENT to see his/her property
#Including basic oprations such as INSERT,DELETE,UPDATE
@user.route("/property/<username>", methods=['GET','POST'])
@login_required
def property(username):
    if current_user.access_id != 1:
        flash("An error has occured. Please contact us!", category='error')
        return render_template("home.html", user=current_user)
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
            
    property_list = []
    for x in current_user.property:
        property_list.append(x.id)

    return render_template("property.html", user=current_user, property = [Property.query.get(x) for x in property_list])

@user.route("/property/<username>/add-property", methods=['GET','POST'])
@login_required
def add_property(username):
    if current_user.access_id != 1:
        flash("An error has occured. Please contact us!", category='error')
        return render_template("home.html", user=current_user)
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

    property_list = []
    for x in current_user.property:
        property_list.append(x.id)   

    if request.method == 'POST':
        if len(request.files.getlist("images")) > 3 :
            flash("Each property can only contain maximum 3 photos. Please try again!", category="error")
            return redirect(url_for('user.property', username=current_user.username))
        
        address_no_postal_code = request.form.get('address_no_postal_code')  
        town = request.form.get('town')     
        flat_type = request.form.get('flat_type')
        flat_model = request.form.get('flat_model')
        block = request.form.get('block')
        street_name = request.form.get('street_name')
        floor_area_sqm = request.form.get('floor_area_sqm')
        price = request.form.get('price')
        postal_code = request.form.get('postal_code')
        storey_range = request.form.get('storey_range')
        description = request.form.get('description')

        new_property = Property(
            agent_id = current_user.id,
            town = town,
            flat_type = flat_type,
            flat_model = flat_model,
            storey_range = storey_range,
            block = block,
            street_name = street_name,
            floor_area_sqm = floor_area_sqm,
            price = price,
            postal_code = postal_code,
            postal_sector = postal_code[:2],
            address_no_postal_code = f'{street_name} BLK {block}',
            time = datetime.now(),

            description = description
        )
        db.session.add(new_property)
        db.session.commit()

        print(new_property.id)
        if 'images' not in request.files:
            new_image = PropertyImage(
                property_id = new_property.id,
                url = "hdb_image0.jpg"
            )
            db.session.add(new_image)
            db.session.commit()
        else:
            num = 1
            for file in request.files.getlist("images"):
                if file.filename == '':
                    new_image = PropertyImage(
                    property_id = new_property.id,
                    url = "hdb_image0.jpg"
                    )
                    db.session.add(new_image)
                    db.session.commit()
                else:
                    extension = file.filename.split('.')[-1]
                    new_filename = "property{}-{}-{}.{}".format(
                        new_property.id, datetime.now().date(), num, extension
                    )
                    num += 1
                    print(new_filename)
                    file.save(os.path.abspath(os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER'),new_filename)))
                    new_image = PropertyImage(
                        property_id = new_property.id,
                        url = new_filename
                    )
                    db.session.add(new_image)
                    db.session.commit()
    
        db.session.commit()
        return redirect(url_for('user.property', username=current_user.username))
            

    return render_template("property_add.html", user=current_user, property = [Property.query.get(x) for x in property_list])

@user.route("/property/delete-property/<property_id>", methods=['GET'])
@login_required
def delete_property(property_id):
    property = Property.query.filter_by(id = property_id).first()

    if property is None:
        flash("The property do not exist in the system!", category='error')
    elif current_user.id != property.agent_id:
        flash("This user don't have the access selected property", category='error')
    else:
        print(property_id)
        for image in property.images:
            if image.address != "hdb_image0.jpg":
                os.remove(os.path.abspath(os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER'),image.address())))
        db.session.delete(property)
        db.session.commit()

    property_list = []
    for x in current_user.property:
        #print(x.id)
        property_list.append(x.id)

    return redirect(url_for('user.property', username = current_user.username))


@user.route('/retrieve_main_picture/<property_id>')
def retrieve_main_picture(property_id):
    filename = PropertyImage.query.filter_by(property_id=property_id).first()
    if filename is not None:
        url = filename.address()
        return send_from_directory(os.path.join(current_app.config.get('UPLOAD_FOLDER')), url)
    else:
        return send_from_directory(os.path.join(current_app.config.get('UPLOAD_FOLDER')), 'hdb_image0.jpg')

@user.route('/retrieve_picture/<image_id>')
def retrieve_picture(image_id):
    filename = PropertyImage.query.filter_by(id=image_id).first()
    if filename is not None:
        url = filename.address()
        return send_from_directory(os.path.join(current_app.config.get('UPLOAD_FOLDER')), url)
    else:
        return send_from_directory(os.path.join(current_app.config.get('UPLOAD_FOLDER')), 'hdb_image0.jpg')

@user.route('/property/<property_id>/property_details')
@login_required
def property_details(property_id):
    property = Property.query.filter_by(id = property_id).first()
    if property is not None:
        images = PropertyImage.query.filter_by(property_id=property_id).all()
        return render_template("property_details.html", property = property, user=current_user, images=images, flat = property)
    else:
        flash('Invalid Access!', category='error')
        return redirect(url_for('views.home'))

