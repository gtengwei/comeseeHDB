from urllib import response
import requests

name = "ZOE TEO XUAN YU"
url = f'https://data.gov.sg/api/action/datastore_search?resource_id=a41ce851-728e-4d65-8dc5-e0515a01ff31&limit=5&q={name}'


response = requests.get(url)

if(response.status_code <= 200 & response.status_code >= 29):
    print(response.json())
    result = response.json()['result']['records']
