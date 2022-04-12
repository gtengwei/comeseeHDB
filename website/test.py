from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
import csv
import pymysql
from pathlib import Path

def main():
    os.chdir("C:/Users/Hannah V/Documents/Github/comeseeHDB/website")
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