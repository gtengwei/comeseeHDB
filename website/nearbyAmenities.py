import math
import json
import pandas as pd
from pathlib import Path
import os
import requests

cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)


def main():
    hdb = pd.read_csv('merged.csv')
    latitude = hdb['latitude'][3421]
    longitude = hdb['longitude'][3421]
    print(latitude, longitude)

    API_KEY = "AIzaSyB3Dn5nm1N8kTQvWiMuQ2PeS_8LI24jUys"
    API_KEY2 = 'Ag6YKlKz_hSG8Drz9iLXx1n3-8r4qRW6XJSt2haPIuZr51AzdiGYq54G5amxfusp'

    specificamenity = {}  # specific amenity
    amenitydict = {}  # dictionaries of amenities
    amenity_list = ['bus_station', 'subway_station',
                    'school', 'restaurant', 'doctor']
    #amenity_list = ['school']
    for amenity in amenity_list:
        url1 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + \
            str(latitude) + "%2C" + str(longitude) + \
            "&radius=500&type="+amenity+"&key=" + API_KEY
        payload = {}
        headers = {}

        response1 = requests.request(
            "GET", url1, headers=headers, data=payload).json()
        length = response1["results"]
        for i in range(len(length)):
            name = response1["results"][i]['name']
            lat_of_nearby = response1['results'][i]['geometry']['location']['lat']
            lon_of_nearby = response1['results'][i]['geometry']['location']['lng']
            url2 = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins="+str(latitude)+","+str(longitude)+"&destinations="+str(lat_of_nearby)+"," + \
                str(lon_of_nearby)+"&travelMode=walking&timeUnit=minute&distanceUnit=km&key=Ag6YKlKz_hSG8Drz9iLXx1n3-8r4qRW6XJSt2haPIuZr51AzdiGYq54G5amxfusp"
            payload = {}
            headers = {}
            response2 = requests.request(
                "GET", url2, headers=headers, data=payload).json()
            nearby_distance = (response2['resourceSets'][0]['resources'][0]
                               ['results'][0]['travelDistance'])*1000  # get distance in metres
            nearby_duration = round(response2['resourceSets'][0]['resources']
                                    [0]['results'][0]['travelDuration'])  # get duration in minutes
            specificamenity[name] = [nearby_distance, nearby_duration]
            amenitydict[amenity] = specificamenity

        print(amenitydict)

    # return amenitydict
    with open("testing.json", "w") as outfile:
        json.dump(amenitydict, outfile)


if __name__ == "__main__":
    main()
