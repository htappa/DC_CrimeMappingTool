import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# build dataframe from api
print('Reading 2019 Crime Incidents data from from OpenDataDC...')
url_crime = 'https://opendata.arcgis.com/datasets/f08294e5286141c293e9202fcd3e8b57_1.geojson'
df_crime = gpd.read_file(url_crime)

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
# add new column to dataframe named 'OFFENSE_GROUP'
df_crime['OFFENSE_GROUP'] = df_crime['OFFENSE'].apply(set_value, args=(offense_dictionary, ))

# define function to filter time of day
def time_of_day():
    time = input("Enter time of day (day, evening, midnight): ")
    time = str(time)
    d = df_crime['SHIFT'] == 'DAY'
    e = df_crime['SHIFT'] == 'EVENING'
    m = df_crime['SHIFT'] == 'MIDNIGHT'
    crime_d = df_crime[d]
    crime_e = df_crime[e]
    crime_m = df_crime[m]
    if time == 'day':
        return crime_d
    elif time == 'evening':
        return crime_e
    elif time == 'midnight':
        return crime_m
    else:
        print('ERROR: Input must be either "day", "evening", or "midnight"')
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
        print('ERROR: Input must be either "violent" or "property"')
        return
df_crime = type_of_offense()


# define dc coordinates for blank map
dc_coordinates = (38.9072, -77.0369)
# create map zoomed in on DC
map = folium.Map(location=dc_coordinates, zoom_start=12)
# add marker clusters to map
mc = MarkerCluster().add_to(map)
# add latitude/longitude to markers
for each in df_crime.iterrows():
    folium.Marker([each[1]['LATITUDE'], each[1]['LONGITUDE']],
                  # add offense and time (start date) to marker popups
                  popup=each[1]['OFFENSE'] + ", " + each[1]['START_DATE']).add_to(mc)
# save map as html file
map.save('map_clustered.html')

# change path to reflect file location and format for webbrowser
filename = 'file:///'+os.getcwd()+'/' + 'map_clustered.html'

# -----------------------------------------------------------------------------------------
# To open the map in a new tab in Google Chrome, use the code below for your respective OS:

# Windows
# chrome_cmd = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s"

# Mac
chrome_cmd = "open -a /Applications/Google\ Chrome.app %s"

# Linux
# chrome_cmd = "/usr/bin/google-chrome %s"
# -----------------------------------------------------------------------------------------

# open map in new browser tab
webbrowser.get(chrome_cmd).open_new_tab(filename)
