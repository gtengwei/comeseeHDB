from geopy.distance import geodesic
import gmaps
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import seaborn.apionly as sns
from scipy.spatial import ConvexHull
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import tabulate
import urllib.request as ur
import warnings
from pathlib import Path
import os
import requests

# import googlemaps
# # client object
# client = googlemaps.Client(key="AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY")

# # area within 500 m
# # lat = 1.3620328,
# # lon = 103.8538267,  # lat lon
# # radius = 500  # radius in meters
# # token = None  # page token for going to next page of search

# # # method 1
# # desirable_places = client.places(query='coffee')

# # # or use way # method 2
# # place_type = 'cafe'
# # desirable_places = client.places(type=place_type)

# # # token for searching next page; to be used in a loop
# # token = desirable_places['next_page_token']

# # print(len(desirable_places))

# # # most avaialable parameters
# # all_fields = ['business_status', 'formatted_address', 'geometry/location', 'name',
# #               'place_id', 'rating', 'types', 'user_ratings_total', 'formatted_phone_number']

# # desirable parameters
# fields = ['place_id', 'name', 'formatted_address']

# # area within 5 km
# # lat lon
# list = ['school', 'restaurants', 'cinema', 'bus stop', 'mrt station']
# amenities = []
# location_bias = 'circle:{}@{},{}'.format(5000, '1.3620328', '103.8538267')
# for i in range(len(list)):
#     place_details = client.find_place(input=list[i],  # or enter a phone number
#                                       input_type='textquery',  # or 'phonenumber'
#                                       location_bias=location_bias,
#                                       fields=fields)
#     amenities.append(place_details)
#     print(place_details)
cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)
hdb = pd.read_csv('latlon_data.csv')
hdb = hdb.drop_duplicates(subset='address')
hdb = hdb.reset_index(drop=True)
print(hdb)
MRT = pd.read_csv('MRT.csv')
LRT = pd.read_csv('LRT.csv')
#MRT['mrt_station_name'] = MRT['mrt_station_name'] + ' Station'
#LRT['lrt_station_name'] = LRT['lrt_station_name'] + ' Station'
list_of_mrt = MRT['mrt_station_name'].values.tolist()
list_of_lrt = LRT['lrt_station_name'].values.tolist()
print(MRT)
print(LRT)
mrt_lat = []
mrt_long = []
for i in range(0, len(list_of_mrt)):
    query_address = list_of_mrt[i]
    query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + \
        str(query_address)+'&returnGeom=Y&getAddrDetails=Y'
    resp = requests.get(query_string)

    data_mrt = json.loads(resp.content)

    if data_mrt['found'] != 0:
        mrt_lat.append(data_mrt["results"][0]["LATITUDE"])
        mrt_long.append(data_mrt["results"][0]["LONGITUDE"])

        print(str(query_address)+",Lat: " +
              data_mrt['results'][0]['LATITUDE'] + " Long: "+data_mrt['results'][0]['LONGITUDE'])

    else:
        mrt_lat.append('NotFound')
        mrt_long.append('NotFound')
        print("No Results")
MRT['latitude'] = mrt_lat
MRT['longitude'] = mrt_long
print(MRT)
# MRT.to_csv('MRT.csv')
list_of_lat = hdb['lat']
list_of_long = hdb['lon']

list_of_mrt_coordinates = []
# Zipping the respective Lat and Long lists together as a list of tuples
list_of_coordinates = []
for lat, long in zip(list_of_lat, list_of_long):
    list_of_coordinates.append((lat, long))
for lat, long in zip(mrt_lat, mrt_long):
    list_of_mrt_coordinates.append((lat, long))

# Distance to nearest MRT

list_of_dist_mrt = []
min_dist_mrt = []

for origin in list_of_coordinates:
    for destination in range(0, len(list_of_mrt_coordinates)):
        list_of_dist_mrt.append(
            geodesic(origin, list_of_mrt_coordinates[destination]).meters)
    shortest = (min(list_of_dist_mrt))
    min_dist_mrt.append(shortest)
    list_of_dist_mrt.clear()
# Storing our distance into our data frame as a new column
hdb['min_dist_mrt'] = min_dist_mrt
print(hdb)
