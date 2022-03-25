import json
import pandas as pd
import urllib.request as ur
import warnings
from pathlib import Path
import os
import requests

cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)

# API_KEY = "AIzaSyB3Dn5nm1N8kTQvWiMuQ2PeS_8LI24jUys"
# #url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522%2C151.1957362&radius=1500&type=restaurant&keyword=cruise&key=YOUR_API_KEY"
# url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + \
#     latitude + "%2C" + longitude + \
#     "&radius=1500&type=school&keyword=school&key=" + API_KEY
# payload = {}
# headers = {}

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)
hdb = pd.read_csv('latlon_data.csv')
# for i in range(len(hdb)):
latitude = str(hdb['lat'][0])
longitude = str(hdb['lon'][0])
convert_url = "https://developers.onemap.sg/commonapi/convert/4326to3414?latitude=" + \
    latitude + "&longitude=" + longitude
converter_response = ur.urlopen(ur.Request(convert_url)).read()
converter_result = json.loads(converter_response)
print(converter_result)
print(type(converter_result))
# sample
#temp_url = "https://developers.onemap.sg/privateapi/commonsvc/revgeocodexy?location=24291.97788882387,31373.0117224489&token=0v9hsciobp1ifa5bgpkin21cs3"
#temp_url = "https://developers.onemap.sg/privateapi/commonsvc/revgeocodexy?location=24291.97788882387,31373.0117224489&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg2MjEsInVzZXJfaWQiOjg2MjEsImVtYWlsIjoiY2hlcnlsdHl4MTdAZ21haWwuY29tIiwiZm9yZXZlciI6ZmFsc2UsImlzcyI6Imh0dHA6XC9cL29tMi5kZmUub25lbWFwLnNnXC9hcGlcL3YyXC91c2VyXC9zZXNzaW9uIiwiaWF0IjoxNjQ4MDY0NDc4LCJleHAiOjE2NDg0OTY0NzgsIm5iZiI6MTY0ODA2NDQ3OCwianRpIjoiYTIyMDMxZGM2MDMwMDkxMTFjZDQ5ZjQ1OGIzM2ViOTYifQ.Fw0KJrE9oIqMxjV7rbID4rySrbIcpXy5ngfW3M7n2Ko&revgeocodexy?&buffer=100&addressType=all"
temp_url = " https://developers.onemap.sg/privateapi/commonsvc/revgeocodexy?location=" + str(converter_result['X']) + "," + str(converter_result['Y']) + \
    "&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg2MjEsInVzZXJfaWQiOjg2MjEsImVtYWlsIjoiY2hlcnlsdHl4MTdAZ21haWwuY29tIiwiZm9yZXZlciI6ZmFsc2UsImlzcyI6Imh0dHA6XC9cL29tMi5kZmUub25lbWFwLnNnXC9hcGlcL3YyXC91c2VyXC9zZXNzaW9uIiwiaWF0IjoxNjQ4MDY0NDc4LCJleHAiOjE2NDg0OTY0NzgsIm5iZiI6MTY0ODA2NDQ3OCwianRpIjoiYTIyMDMxZGM2MDMwMDkxMTFjZDQ5ZjQ1OGIzM2ViOTYifQ.Fw0KJrE9oIqMxjV7rbID4rySrbIcpXy5ngfW3M7n2Ko&revgeocodexy?&buffer=500&addressType=all"
temp_response = ur.urlopen(ur.Request(temp_url)).read()
temp_result = json.loads(temp_response)
temp_values = temp_result['GeocodeInfo']
print(temp_values[0]['BUILDINGNAME'])
print("print keys")
result = pd.DataFrame.from_dict(temp_result)
print(result)
building_name = []
block = []
road = []
postal_code = []
xcoord = []
ycoord = []
latitude = []
longitude = []
for i in range(len(temp_values)):
    building_name.append(temp_values[i]['BUILDINGNAME'])
    block.append(temp_values[i]['BLOCK'])
    road.append(temp_values[i]['ROAD'])
    postal_code.append(temp_values[i]['POSTALCODE'])
    xcoord.append(temp_values[i]['XCOORD'])
    ycoord.append(temp_values[i]['YCOORD'])
    latitude.append(temp_values[i]['LATITUDE'])
    longitude.append(temp_values[i]['LONGITUDE'])
tempdf = pd.DataFrame({'Ang Mo Kio': {'building_name': building_name,
                                      'block': block,
                                      'road': road,
                                      'postal_code': postal_code,
                                      'xcoord': xcoord,
                                      'ycoord': ycoord,
                                      'latitude': latitude,
                                      'longitude': longitude}})
print(tempdf)
tempdf.to_csv("nearbyAmenities.csv", index=False)
