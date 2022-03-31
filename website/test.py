from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
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
    town = Column(String(150))
    flat_type = Column(String(150))
    block = Column(String(150))
    street_name = Column(String(150))
    storey_range = Column(String(150))
    floor_area_sqm = Column(Float)
    flat_model = Column(String(150))
    lease_commence_date = Column(Date)
    remaining_lease = Column(Float)
    resale_price = Column(Float)


def main():
    os.chdir("C:/Users/Hannah V/Documents/github/comeseeHDB/website")
    df = pd.read_csv('merged.csv')
    # print(df.dtypes)
    df['price_per_sqm'] = round(
        df['resale_price'] / df['floor_area_sqm'])
    # print(df['price_per_square_metre'])
    df['block'].astype(str)
    df['street_name'].astype(str)
    df['address'] = df['street_name'] + ' BLK ' + df['block']
    df['numOfFavourites'] = 0
    # print(df['address'])
    # writing into the file
    #df.drop('price_per_square_metre', axis=1, inplace=True)
    df.sort_values(by=['address'], ascending=True, inplace=True)
    df.to_csv("merged.csv", index=False)

def create_flat_csv(): 
    engine = create_engine('mysql+pymysql://root:Clutch123!@localhost/mysql_database?charset=utf8') # enter your password and database names here
    #Base.metadata.create_all(engine)
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    df = pd.read_csv('merged.csv')    
    df.to_sql(con=engine, index_label='id', name="flat", if_exists='replace')


def create_mysql_database():
    database = pymysql.connect(
        host="localhost",
        user="root",
        passwd="Clutch123!"
    )
    cursor = database.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS mysql_database")

        
if __name__ == "__main__":
    # main()
    #create_database()
    create_flat_csv()
    # add_test_data()
