## To create relational schema and the attributes of the schema

from tkinter import CASCADE
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from hashlib import md5
from sqlalchemy import Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

## To migrate database
class Review(db.Model):
    _N = 6

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    data = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'), nullable=False)
    numOfLikes = db.Column(db.Integer, default=0)
    numOfParentLikes = db.Column(db.Integer, default=0)
    likes = db.relationship('ReviewLikes')
    review_path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('review.id'))
    reply = db.relationship('Review', cascade="all,delete", backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.review_path + '.' if self.parent else ''
        self.review_path = prefix + '{:0{}d}'.format(self.id, self._N)
        db.session.commit()
        
    def level(self):
        if self.review_path is None:
            return 0
        return len(self.review_path) // self._N - 1


class FlatLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'))

class ReviewLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)

# Table for User entity
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    access_id = db.Column(db.Integer(), nullable=False, default=0)
    postal_code = db.Column(db.Integer)
    postal_code_change = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    likes = db.relationship('FlatLikes')
    email_verified = db.Column(db.Boolean(), nullable=False, default=False)
    email_verified_date = db.Column(db.DateTime(timezone=True), default = None)
    reviews = db.relationship('Review', backref = 'user', passive_deletes=True)
    review_likes = db.relationship('ReviewLikes')
    property = db.relationship('Property', backref = 'user', passive_deletes=True)
    propertyLikes = db.relationship('PropertyLikes', backref = 'user', passive_deletes=True)

    def get_token(self,expires_sec=120):
        serial=Serializer(current_app.config['SECRET_KEY'],expires_in = expires_sec)
        return serial.dumps({'user_id':self.id}).decode('utf-8')
    
    ## Function does not use any property of User class, hence we use staticmethod
    @staticmethod 
    # To verify the token from the user
    def verify_token(token):
        serial=Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}'.format(
            digest, size)
    



#Base = declarative_base()
class Flat(db.Model):
    # Inform SQLAlchemy of the column names and its attributes
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    month = db.Column(db.String(150)) 
    town = db.Column(db.String(150))
    flat_type = db.Column(db.String(150))
    block = db.Column(db.String(150))
    street_name = db.Column(db.String(150))
    storey_range = db.Column(db.String(150))
    floor_area_sqm = db.Column(db.Float)
    flat_model = db.Column(db.String(150))
    lease_commence_date = db.Column(db.String(150))
    remaining_lease = db.Column(db.String(150))
    resale_price = db.Column(db.Integer) 
    price_per_sqm = db.Column(db.Integer)
    address = db.Column(db.String(150))
    resale_price = db.Column(Float)
    numOfLikes = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    postal_code = db.Column(db.Integer)
    postal_sector = db.Column(db.Integer)
    address_no_postal_code = db.Column(db.String(150))
    image = db.Column(db.String(150))
    reviews = db.relationship('Review', backref = 'flat', passive_deletes=True)
    likes = db.relationship('FlatLikes', backref = 'flat', passive_deletes=True)   

def create_Flat_table():
    #To create the table in the database (SQLite)
    engine = create_engine('sqlite:///website/database.db')
    db.Model.metadata.create_all(engine)
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    df = pd.read_csv('merged.csv')
    df.to_sql(con=engine, name=Flat.__tablename__, if_exists='replace')

class Property(db.Model):
    # Inform SQLAlchemy of the column names and its attributes
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    town = db.Column(db.String(150))
    flat_type = db.Column(db.String(150))
    flat_model = db.Column(db.String(150))
    block = db.Column(db.String(150))
    storey_range = db.Column(db.String(150))
    street_name = db.Column(db.String(150))
    floor_area_sqm = db.Column(db.Float)
    price = db.Column(Float) 
    numOfLikes = db.Column(db.Integer, default=0)
    postal_code = db.Column(db.Integer)
    postal_sector = db.Column(db.Integer)
    address_no_postal_code = db.Column(db.String(150))
    time = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    images = db.relationship('PropertyImage', backref = 'property', cascade="all,delete")
    description = db.Column(db.String(3000))
    likes = db.relationship('PropertyLikes', backref = 'property',  cascade="all,delete")   

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id', ondelete='CASCADE'))
    url = db.Column(db.String(256))
    upload_time = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())

    def address(self):
        return self.url

class PropertyLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    prop_id = db.Column(db.Integer, db.ForeignKey('property.id', ondelete='CASCADE'))