## To create relational schema and the attributes of the schema
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from hashlib import md5
from random import randint
from datetime import datetime

## Table for Note entity (To be changed to placeholders/HDB flats)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Table for User entity
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    postal_code = db.Column(db.String(150))
    postal_code_change = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    reviews = db.relationship('Review')
    email_verified = db.Column(db.Boolean(), nullable=False, default=False)
    email_verified_date = db.Column(db.DateTime(timezone=True))

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
    
    
