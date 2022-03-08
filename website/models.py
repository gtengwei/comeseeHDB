## To create relational schema and the attributes of the schema
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from hashlib import md5
from test import *
from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
from pathlib import Path
from sqlalchemy.dialects.mysql import BIGINT

## To migrate database
class Review(db.Model):
    id = db.Column(BIGINT, primary_key=True, nullable=False)
    data = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(BIGINT, db.ForeignKey('user.id'), nullable=False)
    flat_id = db.Column(BIGINT, db.ForeignKey('flat.id'), nullable=False)

# Table for User entity
class User(db.Model, UserMixin):
    id = db.Column(BIGINT, primary_key=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    postal_code = db.Column(db.String(150))
    postal_code_change = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    email_verified = db.Column(db.Boolean(), nullable=False, default=False)
    email_verified_date = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    reviews = db.relationship('Review', backref = 'user', passive_deletes=True)

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
    #Tell SQLAlchemy what the table name is and if there's any table-specific arguments it should know about
    #__tablename__ = 'HDB_Flats'
    #__table_args__ = {'sqlite_autoincrement': True}
    #tell SQLAlchemy the name of column and its attributes:
    id = db.Column(BIGINT, primary_key=True, nullable=False)
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
    reviews = db.relationship('Review', backref = 'flat', passive_deletes=True)
    

def create_Flat_table():
    #To create the table in the database (SQLite)
    #engine = create_engine('sqlite:///website/database.db')
    #db.Model.metadata.create_all(engine)
    #os.chdir("C:/Users/tengwei/Desktop/github/comeseeHDB/website")
    #df = pd.read_csv('test.csv')
    #df.to_sql(con=engine, index_label='id', name=Flat.__tablename__, if_exists='replace')

    # To create the table in the database (MySQL)
    engine = create_engine('mysql://root:Clutch123!@localhost/mysql_database?charset=utf8') # enter your password and database names here
    db.Model.metadata.create_all(engine)
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)    
    df = pd.read_csv('test.csv')    
    df.to_sql(con=engine, index_label='id', name="flat", if_exists='replace')
    
