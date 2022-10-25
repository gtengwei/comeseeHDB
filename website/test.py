# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# import pandas as pd
import os
# import csv
from pathlib import Path
# from models import User
# from werkzeug.security import generate_password_hash
# from models import db
# from datetime import datetime
import sqlite3

# #Base = declarative_base()

# def create_HDB_Flats_table():
#     # This will create the table in the database
#     engine = create_engine('sqlite:///website/database.db')
#     Base.metadata.create_all(engine)
#     cwd = Path(__file__).parent.absolute()
#     os.chdir(cwd)
#     df = pd.read_csv('merged.csv')
#     # print(df.dtypes)
#     df['price_per_sqm'] = round(
#         df['resale_price'] / df['floor_area_sqm'])
#     # print(df['price_per_square_metre'])
#     df['block'].astype(str)
#     df['street_name'].astype(str)
#     df['postal_code'] = df['postal_code'].astype(str)
#     df['address'] = df['street_name'] + ' BLK ' + df['block'] + ' ' + df['postal_code']
#     df['address_no_postal_code'] = df['street_name'] + ' BLK ' + df['block']
#     df['numOfFavourites'] = 0
#     # print(df['address'])
#     # writing into the file
#     #df.drop('address2', axis=1, inplace=True)
#     df.sort_values(by=['address'], ascending=True, inplace=True)
#     df.to_csv("merged.csv", index=False)

# def append_image():
#     # read csv
#     df = pd.read_csv('merged.csv')
#     df['image'] = None
#     for i in range(len(df)):
#         count = i % 6
#         df.at[i, 'image'] = 'hdb_image'+str(count)+'.jpg'

#     #df.drop('Unnamed: 0', axis=1, inplace=True)
#     df.to_csv('merged.csv', index=False)

# def create_user():
#     email = 'test@gmail.com'
#     username = 'test'
#     postal_code = 75
#     password1 = '12345678'

#     new_user = User(email=email, username = username, postal_code = postal_code,
#                 password=generate_password_hash(password1, method='sha256'), email_verified = True,
#                 email_verified_date = datetime.now())
#     db.session.add(new_user)
#     db.session.commit()
#     return

def delete_record():
    cwd = Path(__file__).parent.absolute()
    os.chdir(cwd)
    # print(os.getcwd())
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    # myquery = (
    #     "SELECT id FROM Flat ORDER BY numOfLikes DESC;")
    myquery = ( "DELETE FROM Property_Image WHERE property_id = 6 or property_id = 7;")
    c.execute(myquery)
    conn.commit()
    myquery = ("SELECT * FROM Property;")
    c.execute(myquery)
    result = c.fetchall()
    print(result)

if __name__ == "__main__":
    # main()
    #create_database()
    #create_HDB_Flats_table()
    #create_user()
    delete_record()
