import pandas as pd
from pathlib import Path
import os
import requests

cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)

# read csv
olddf = pd.read_csv('List of HDB Address.csv')

# include address coumn
olddf['Address'] = olddf['block'] + " " + olddf['street_name']
df = olddf.drop_duplicates(['Address'])
df = df.reset_index(drop=True)
print(df)
addresslist = list(df['Address'])
print(addresslist)

# get coordinates and postal code based on address


def getcoordinates(address):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal=' +
                       address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results']) > 0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE'], resultsdict['results'][0]['POSTAL']
    else:
        return None


coordinateslist = []
count = 0
failed_count = 0

# append coordinates and address into DataFrame
for address in addresslist:
    try:
        if len(getcoordinates(address)) > 0:
            count = count + 1
            print('Extracting', count, 'out of', len(addresslist), 'addresses')
            coordinateslist.append(getcoordinates(address))
    except:
        count = count + 1
        failed_count = failed_count + 1
        print('Failed to extract', count, 'out of',
              len(addresslist), 'addresses')
        coordinateslist.append(None)
print('Total Number of Addresses With No Coordinates', failed_count)
df_coordinates = pd.DataFrame(coordinateslist)
# combined coordinates and postal code with original dataframe
df_combined = pd.concat([df, df_coordinates], axis=1, join='outer')
df_combined = df_combined .rename(
    columns={0: 'Latitude', 1: 'Longitude', 2: 'Postal_Code'})
df_combined = df_combined[['Address', 'Latitude', 'Longitude', 'Postal_Code']]
df_combined = pd.merge(olddf, df_combined, on='Address')
# convert dataframe into csv
# df_combined.to_csv('new_data.csv')

# read csv
data = pd.read_csv("new_data.csv")

# add new columns and edit column names
data['price_per_sqm'] = round(
    data['resale_price'] / data['floor_area_sqm'])
data = data.rename(columns={'Address': 'address', 'Latitude': 'latitude',
                            'Longitude': 'longitude', 'Postal_Code': 'postal_code'})
data['postal_sector'] = data.postal_code.str.slice(0, 2)
col_title = ['month', 'town', 'flat_type', 'block', 'street_name', 'storey_range', 'floor_area_sqm', 'flat_model', 'lease_commence_date',
             'remaining_lease', 'resale_price', 'price_per_sqm', 'address', 'latitude', 'longitude', 'postal_code', 'postal_sector']
data = data.reindex(columns=col_title)
data['numOfFavourites'] = 0
# convert to csv
#data.to_csv("new_data.csv", index=False)


# removing duplicated flats
duplicate = data.groupby(['address', 'storey_range', 'flat_type'])['month'].apply(
    list).reset_index(name='month_list')
month = list(duplicate['month_list'])
new_month_list = []
for i in range(len(month)):
    new_month_list.append(max(month[i]))
print(len(new_month_list))
new_df = pd.DataFrame(new_month_list, columns=['month'])
print("DEBUG", new_df)
#duplicate['month_list'] = max(duplicate['month_list'])
duplicate['month_list'] = new_df
duplicate = duplicate.rename(columns={'month_list': 'month'})

duplicate = pd.merge(duplicate, data, on=[
                     'address', 'storey_range', 'flat_type', 'month'])
duplicate = duplicate.drop_duplicates(
    subset=['address', 'storey_range', 'flat_type', 'month'], keep='first')
duplicate = duplicate.reset_index(drop=True)

# convert newest dataframe into csv
#duplicate.to_csv('merged.csv', index=False)
