import time

import pandas as pd
import tqdm
from geopy.geocoders import Nominatim

from service.constants import *

geolocator = Nominatim(user_agent="agent")


def add_coords(data, coords):
    for address in tqdm.tqdm(data):
        try:
            location = geolocator.geocode(address)
            coords['Latitude'].append(location.latitude)
            coords['Longitude'].append(location.longitude)
            coords['Address'].append(address)
            time.sleep(0.5)
        except AttributeError as e:
            print(e)
            print('Error:', address)


df = pd.read_csv(DATASET_PATH)
coords_dict = {'Address': [], 'Latitude': [], 'Longitude': []}

countries = df[df[COUNTRY_REGION].notnull()][COUNTRY_REGION].unique()
add_coords(countries, coords_dict)

coords_df = pd.DataFrame(coords_dict)
coords_df.to_csv(GPS_COORDS_PATH, index=False)

states = df[df[COUNTRY_REGION].notnull() & df[STATE_REGION].notnull()][[COUNTRY_REGION, STATE_REGION]].drop_duplicates()
states = states[COUNTRY_REGION] + ', ' + states[STATE_REGION]
add_coords(states, coords_dict)

coords_df = pd.DataFrame(coords_dict)
coords_df.to_csv(GPS_COORDS_PATH, index=False)

cities = df[df[COUNTRY_REGION].notnull() & df[STATE_REGION].notnull() & df[CITY].notnull()][
    [COUNTRY_REGION, STATE_REGION, CITY]].drop_duplicates()
cities = cities[COUNTRY_REGION] + ', ' + cities[STATE_REGION] + ', ' + cities[CITY]
add_coords(cities, coords_dict)

coords_df = pd.DataFrame(coords_dict)
coords_df.to_csv(GPS_COORDS_PATH, index=False)
