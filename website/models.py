## To create relational schema and the attributes of the schema

from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from hashlib import md5
from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
from pathlib import Path
from sqlalchemy.dialects.mysql import BIGINT
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

## To migrate database
class Review(db.Model):
    # id = db.Column(db.Integer, primary_key=True, nullable=False)
    id = db.Column(BIGINT, primary_key=True, nullable=False) # for mysql
    data = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'), nullable=False)
    user_id = db.Column(BIGINT, db.ForeignKey('user.id'), nullable=False) # for mysql
    flat_id = db.Column(BIGINT, db.ForeignKey('flat.id'), nullable=False) # for mysql

class Favourites(db.Model):
    id = db.Column(BIGINT, primary_key=True)
    user_id = db.Column(BIGINT, db.ForeignKey('user.id'))
    flat_id = db.Column(BIGINT, db.ForeignKey('flat.id'))

# Table for User entity
class User(db.Model, UserMixin):
    # id = db.Column(db.Integer, primary_key=True, nullable=False)
    id = db.Column(BIGINT, primary_key=True, nullable=False) # for mysql
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    postal_code = db.Column(db.String(150))
    postal_code_change = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    favourites = db.relationship('Favourites')
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
    #tell SQLAlchemy the name of column and its attributes:
    # id = db.Column(db.Integer, primary_key=True, nullable=False)
    id = db.Column(BIGINT, primary_key=True, nullable=False) # for mysql
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
    numOfFavourites = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    postal_code = db.Column(db.Integer)
    postal_sector = db.Column(db.Integer)
    address_no_postal_code = db.Column(db.String(150))
    reviews = db.relationship('Review', backref = 'flat', passive_deletes=True)
    favourites = db.relationship('Favourites', backref = 'flat', passive_deletes=True)   

def create_Flat_table():
    #To create the table in the database (SQLite)
    engine = create_engine('mysql+pymysql://root:Clutch123!@localhost/mysql_database?charset=utf8')
    db.Model.metadata.create_all(engine)
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    df = pd.read_csv('merged.csv')
    df.to_sql(con=engine, index_label='id', name=Flat.__tablename__, if_exists='replace')

    '''
    # To create the table in the database (MySQL)
    # engine = create_engine('mysql+pymysql://root:Clutch123!@/mysql_database?unix_socket=/cloudsql/comesee-hdb:asia-southeast1:comeseehdb-database')
    engine = create_engine('mysql+pymysql://root:Clutch123!@localhost/mysql_database?charset=utf8') # enter your password and database names here
    db.Model.metadata.create_all(engine)
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)    
    df = pd.read_csv('test.csv')    
    df.to_sql(con=engine, index_label='id', name="flat", if_exists='replace')
    '''
    

'''def create_Flat_table():
    #This will create the table in the database
    engine = create_engine('sqlite:///website/database.db')
    db.Model.metadata.create_all(engine)
    os.chdir('C:/Users/Yap Xuan Ying/Documents/WORK!!!/comeseeHDB/website')
    df = pd.read_csv('merged.csv')
    df.to_sql(con=engine, index_label='id', name=Flat.__tablename__, if_exists='replace')'''
