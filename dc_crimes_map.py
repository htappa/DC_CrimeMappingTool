import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# build dataframe from api
print('Reading 2019 Crime Incidents data from from OpenDataDC...')
url_crime = 'https://opendata.arcgis.com/datasets/f08294e5286141c293e9202fcd3e8b57_1.geojson'
df_crime = gpd.read_file(url_crime)

# change date format
df_crime.START_DATE = pd.to_datetime(df_crime.START_DATE, format='%Y/%m/%d %H:%M:%S')

# create time of day column
hours = df_crime['START_DATE'].dt.hour
bins = [-1, 4, 9, 17, 21]
labels = ['night', 'morning', 'afternoon', 'evening', 'night']
df_crime['time_of_day'] = np.array(labels)[np.array(bins).searchsorted(hours)-1]

# create new column for violent crimes and property crimes where:
#   violent = ASSAULT W/DANGEROUS WEAPON, HOMICIDE, ROBBERY, SEX ABUSE
#   property = MOTOR VEHICLE THEFT, THEFT F/AUTO, THEFT/OTHER, BURGLARY, ARSON

# define function to map values for new column
def set_value(row_number, assigned_value):
    return assigned_value[row_number]
# create dictionary of offenses
offense_dictionary = {'ASSAULT W/DANGEROUS WEAPON': 'violent', 'HOMICIDE': 'violent', 'ROBBERY': 'violent',
                      'SEX ABUSE': 'violent', 'THEFT/OTHER': 'property', 'THEFT F/AUTO': 'property',
                      'MOTOR VEHICLE THEFT': 'property', 'BURGLARY': 'property', 'ARSON': 'property'}
# add new column to dataframe for offense grouping
df_crime['OFFENSE_GROUP'] = df_crime['OFFENSE'].apply(set_value, args=(offense_dictionary, ))

# define function to filter time of day
def time_of_day():
    time = input("Enter time of day (morning, afternoon, evening, night): ")
    time = str(time)
    m = df_crime['time_of_day'] == 'morning'
    a = df_crime['time_of_day'] == 'afternoon'
    e = df_crime['time_of_day'] == 'evening'
    n = df_crime['time_of_day'] == 'night'
    crime_m = df_crime[m]
    crime_a = df_crime[a]
    crime_e = df_crime[e]
    crime_n = df_crime[n]
    if time == 'morning':
        return crime_m
    elif time == 'afternoon':
        return crime_a
    elif time == 'evening':
        return crime_e
    elif time == 'night':
        return crime_n
    else:
        print('ERROR: Input must be either "morning", "afternoon", "evening", "night" (case sensitive)')
        return
df_crime = time_of_day()

# define function to filter offense type
def type_of_offense():
    offense = input("Enter offense type (violent, property): ")
    offense = str(offense)
    v = df_crime['OFFENSE_GROUP'] == 'violent'
    p = df_crime['OFFENSE_GROUP'] == 'property'
    crime_v = df_crime[v]
    crime_p = df_crime[p]
    if offense == 'violent':
        return crime_v
    elif offense == 'property':
        return crime_p
    else:
        print('ERROR: Input must be either "violent" or "property" (case sensitive)')
        return
df_crime = type_of_offense()


# define dc coordinates for blank map
dc_coordinates = (38.9072, -77.0369)
# create map zoomed in on DC
map = folium.Map(location=dc_coordinates, zoom_start=12)
# add marker clusters to map
mc = MarkerCluster().add_to(map)
# change data type of date column to string
df_crime.START_DATE = df_crime.START_DATE.apply(lambda x: x.strftime('%m/%d/%Y %H:%M'))
# add latitude/longitude to markers
for each in df_crime.iterrows():
    folium.Marker([each[1]['LATITUDE'], each[1]['LONGITUDE']],
                  # add offense and time (start date) to marker popups
                  popup=each[1]['OFFENSE'] + ", " + each[1]['START_DATE']).add_to(mc)
# save map as html file
map.save('map_clustered.html')

# change path to reflect file location and format for webbrowser
filename = 'file:///' + os.getcwd() + '/' + 'map_clustered.html'

# -----------------------------------------------------------------------------------------
# To open the map in a new tab in Google Chrome, use the code below for your respective OS:

# Windows
# webbrowser.open_new_tab(filename)

# Mac
cmd = 'open -a /Applications/Google\ Chrome.app %s'
webbrowser.get(cmd).open_new_tab(filename)

# -----------------------------------------------------------------------------------------
