from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import pandas as pd
import os

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
    os.chdir("C:/Users/tengwei/Desktop/github/comeseeHDB/website")
    df = pd.read_csv('test.csv')
    df.to_sql(con=engine, index_label='id',
              name=HDB_Flats.__tablename__, if_exists='replace')


def main():
    os.chdir("C:/Users/tengwei/Desktop/github/comeseeHDB/website")
    df = pd.read_csv('test.csv')
    # print(df.dtypes)
    df['price_per_sqm'] = round(
        df['resale_price'] / df['floor_area_sqm'])
    # print(df['price_per_square_metre'])
    df['block'].astype(str)
    df['street_name'].astype(str)
    df['address'] = df['street_name'] + ' BLK ' + df['block']
    # print(df['address'])
    # writing into the file
    #df.drop('price_per_square_metre', axis=1, inplace=True)
    df.to_csv("test.csv", index=False)


if __name__ == "__main__":
    main()
