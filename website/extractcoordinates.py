# Import modules
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

# Settings

# Read data
cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)
hdb = pd.read_csv('test.csv')


# Create addresses
hdb['full_address'] = hdb.block + ' ' + hdb.street_name
hdb['search_address'] = hdb.block + '+' + \
    hdb.street_name.str.replace(' ', '+') + '+SINGAPORE'

# Extract search addresses
all_adds = hdb.search_address.unique()
print(hdb['search_address'][0])
print(all_adds[0])


# # Set parameters
APP_ID = '8jbALthtA2oJZk4EfcKIsg'
APP_CODE = 'eEak1NMA7WsImXCJDO47R7lzQF7M6DR9SgvdF9XtJrqkWW0541OyZgYncSCgsZG_HRWjLqy2s_n-oPXXM5OefQ'

# Define function to extract average location
# Takes a dictionary object
# Returns the average of display position and navigation position in a dictionary


def get_loc(result):

    # Output
    output = dict()

    if len(result['Response']['View']) > 0:

        # Get display position lat/long
        lat_dp = result['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
        lon_dp = result['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']

        # Get navigation position lat/long
        lat_np = result['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Latitude']
        lon_np = result['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Longitude']

        # Configure output
        output['lat'] = (lat_dp + lat_np) / 2
        output['lon'] = (lon_dp + lon_np) / 2

    else:

        # Configure output
        output['lat'] = np.nan
        output['lon'] = np.nan

    return output


# Initialise results
all_latlon = []

# Loop through to get lat lon
for i in range(len(hdb)):

    # Extract address
    temp_add = hdb['search_address'][i]

    # Configure URL
    temp_url = 'https://geocoder.ls.hereapi.com/6.2/geocode.json' + \
        '?apiKey=pbn2lpRmqJjeeR3TYiRq8OcQu5iQzCux84PY2NrfLXs' + \
        '&searchtext=' + temp_add

    # Pull data
    temp_response = ur.urlopen(ur.Request(temp_url)).read()
    temp_result = json.loads(temp_response)

    # Process data
    temp_latlon = get_loc(temp_result)

    # Add address
    temp_latlon['address'] = temp_add

    # Append
    all_latlon.append(temp_latlon)

    # Update
    print(str(i) + '. ', 'Getting data for: ' + str(temp_add))

# Convert to data frame
full_latlon = pd.DataFrame(all_latlon)

# Save
full_latlon.to_csv('latlon_data.csv', index=False)

# Load data
map_latlon = pd.read_csv('latlon_data.csv')

# View
map_latlon.head()
