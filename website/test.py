from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
import mysql.connector
import csv
import pymysql
from pathlib import Path

Base = declarative_base()


class HDB_Flats(Base):
    # Tell SQLAlchemy what the table name is and if there's any table-specific arguments it should know about
    __tablename__ = 'HDB_Flats'
    __table_args__ = {'sqlite_autoincrement': True}
    # tell SQLAlchemy the name of column and its attributes:
    id = Column(Integer, primary_key=True, nullable=False)
    month = Column(Integer)
    town = Column(String)
    flat_type = Column(String)
    block = Column(String)
    street_name = Column(String)
    storey_range = Column(String)
    floor_area_sqm = Column(Float)
    flat_model = Column(String)
    lease_commence_date = Column(Date)
    remaining_lease = Column(Float)
    resale_price = Column(Float)


def create_HDB_Flats_table():
    # This will create the table in the database
    engine = create_engine('sqlite:///website/database.db')
    Base.metadata.create_all(engine)
    file_name = 'test.csv'
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    df = pd.read_csv('merged.csv')
    # print(df.dtypes)
    df['price_per_sqm'] = round(
        df['resale_price'] / df['floor_area_sqm'])
    # print(df['price_per_square_metre'])
    df['block'].astype(str)
    df['street_name'].astype(str)
    df['postal_code'] = df['postal_code'].astype(str)
    df['address'] = df['street_name'] + ' BLK ' + df['block'] + ' ' + df['postal_code']
    df['address_no_postal_code'] = df['street_name'] + ' BLK ' + df['block']
    df['numOfFavourites'] = 0
    # print(df['address'])
    # writing into the file
    #df.drop('address2', axis=1, inplace=True)
    df.sort_values(by=['address'], ascending=True, inplace=True)
    df.to_csv("merged.csv", index=False)



def create_mysql_database():
    database = pymysql.connect(
        host="localhost",
        user="root",
        passwd="Clutch123!"
    )
    cursor = database.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS mysql_database")

