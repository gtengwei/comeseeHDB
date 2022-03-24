from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os
from pathlib import Path
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

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


def create_HDB_Flats_table(engine):
    # This will create the table in the database
    engine = create_engine('sqlite:///website/database.db')
    Base.metadata.create_all(engine)
    file_name = 'test.csv'
    cwd = Path(__file__).parent.absolute()
    print(cwd)
    os.chdir(cwd)
    df = pd.read_csv('test.csv')
    df.to_sql(con=engine, index_label='id',
              name=HDB_Flats.__tablename__, if_exists='replace')


def main():
    cwd = Path(__file__).parent.absolute()
    print(cwd)
    os.chdir(cwd)
    df = pd.read_csv('test.csv')
    # print(df.dtypes)
    # df['price_per_sqm'] = round(
    #     df['resale_price'] / df['floor_area_sqm'])
    # # print(df['price_per_square_metre'])
    # df['block'].astype(str)
    # df['street_name'].astype(str)
    # df['address'] = df['block'] + ' ' + df['street_name']
    # df['address'].astype(str)
    # print(df['address'])
    # writing into the file
    #df.drop('price_per_square_metre', axis=1, inplace=True)
    # 1 - conveneint function to delay between geocoding calls
    #locator = Nominatim(user_agent="cheryltyx17@gmail.com")
    #df['latitude'] = None
    #df['longitude'] = None
    # for i in range(50):
    #location = locator.geocode(df['address'][i])
    # if(location != None):
    # print(location.latitude)
    # print(location.longitude)
    #df.at[i, 'latitude'] = location.latitude
    #df.at[i, 'longitude'] = location.longitude
    # print(df[:50])
    #df = df.drop(columns="latitude")
    #df = df.drop(columns="longitude")
    #df.to_csv("test.csv", index=False)
    #duplicated = df.duplicated()
    df = df.drop_duplicates()
    print(df)


if __name__ == "__main__":
    main()
