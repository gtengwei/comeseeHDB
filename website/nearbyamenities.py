import pandas as pd
from pathlib import Path
import os
import requests
import json

cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)
flat = pd.read_csv('merged.csv')
flat = flat.drop_duplicates(subset=['address'])
ind_list = [i for i in range(3000, 3500)]
flat = flat.iloc[ind_list]
print(flat)
for i in range(len(flat)):
    print(f"{i} out of {len(flat)} flats")
    latitude = flat['latitude'].values[i]
    longitude = flat['longitude'].values[i]
    address = flat['address'].values[i]
    print(f"latitude: {latitude}, longitude: {longitude}, address: {address}")
    filename = 'amenity_database.json'

    with open(filename, 'r') as f:
        data = json.load(f)
        # print(address)
        # print(data.get(address))
        if address in data.keys():
            print("hlelo")
            continue
        else:
            API_KEY = "AIzaSyDpj-F6MN21wdrhuqb9yi7jTLuP9hTwwoc"
            API_KEY2 = 'Ag6YKlKz_hSG8Drz9iLXx1n3-8r4qRW6XJSt2haPIuZr51AzdiGYq54G5amxfusp'

            specificamenity = {}  # specific amenity
            amenitydict = {}  # dictionaries of amenities
            amenity_list = ['bus_station', 'subway_station',
                            'school', 'restaurant', 'doctor']
            #amenity_list = ['school']
            for amenity in amenity_list:
                specificamenity = {}  # specific amenity
                url1 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + \
                    str(latitude) + "%2C" + str(longitude) + \
                    "&radius=500&type="+amenity+"&key=" + API_KEY
                print(url1)
                payload = {}
                headers = {}

                response1 = requests.request(
                    "GET", url1, headers=headers, data=payload).json()
                length = response1["results"]
                for i in range(len(length)):
                    name = response1["results"][i]['name']
                    print(name)
                    if len(name) > 30:
                        continue
                    if (amenity == 'school') and ('School' not in name):
                        continue
                    lat_of_nearby = response1['results'][i]['geometry']['location']['lat']
                    lon_of_nearby = response1['results'][i]['geometry']['location']['lng']
                    url2 = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins="+str(latitude)+","+str(longitude)+"&destinations="+str(lat_of_nearby)+"," + \
                        str(lon_of_nearby) + \
                        "&travelMode=walking&timeUnit=minute&distanceUnit=km&key="+API_KEY2
                    payload = {}
                    headers = {}
                    response2 = requests.request(
                        "GET", url2, headers=headers, data=payload).json()
                    nearby_distance = round((response2['resourceSets'][0]['resources'][0]
                                            ['results'][0]['travelDistance'])*1000)  # get distance in metres
                    nearby_duration = round(response2['resourceSets'][0]['resources']
                                            [0]['results'][0]['travelDuration'])  # get duration in minutes
                    specificamenity[name] = [nearby_distance, nearby_duration]
                    amenitydict[amenity] = specificamenity

                print(amenitydict)
        data[address] = amenitydict
        with open('amenity_database.json', 'w') as f:
            json.dump(data, f, indent=4)
