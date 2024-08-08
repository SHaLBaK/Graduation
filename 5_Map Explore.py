# Packages
import folium.map
import pandas as pd
import matplotlib.pyplot as plt
import folium
import os
import geopandas as gpd
from streamlit_folium import st_folium
import streamlit as st
from shapely import wkt
from pyproj import CRS, Transformer

# Pages setup
st.set_page_config(layout="wide")
st.title('Explore Map')
st.subheader ('Use sidebar checkbox to select layers to show')
st.markdown("""<style> section[data-testid="stSidebar"][aria-expanded="true"]{min-width: 100px;max-width: 250px; display: inline; } </style>""",
             unsafe_allow_html=True)

# Loading Data
with st.spinner("Loading Data ... "):
        if 'Land_use' not in st.session_state:
                st.session_state.Land_use = gpd.read_file(r'Data\Land_use\Land_use.shp'  )

        if 'Popu' not in st.session_state:
                st.session_state.Popu = gpd.read_file(r'Data\Popu\Popu.shp'  )

        if 'DTCA' not in st.session_state:
                st.session_state.DTCA = gpd.read_file(r'Data\DTCA\DTCA.shp'  )

        if 'Sidewalk' not in st.session_state:
                st.session_state.Sidewalk = gpd.read_file(r'Data\Sidewalk\Sidewalk.shp'  )

        if 'Ramps' not in st.session_state:
                st.session_state.Ramps = gpd.read_file(r'Data\Ramps\Ramps.shp'  )

        if 'Flood' not in st.session_state:
                st.session_state.Flood = gpd.read_file(r'Data\Flood\Flood.shp')
                #Flood = pd.read_csv(r'Data\Flood\Flood.shp')# , header= 0 )
                #st.session_state.Flood = gpd.GeoDataFrame(Flood , geometry='geometry' , crs = 2276 )              

        if 'Trucks' not in st.session_state:
                st.session_state.Trucks = gpd.read_file(r'Data\Trucks\Trucks.shp'  )

        if 'Speed' not in st.session_state:
                st.session_state.Speed = gpd.read_file(r'Data\Speed\Speed.shp'  )

        if 'boundry' not in st.session_state:
        # Getting the city boundries:
                cities = gpd.read_file('https://data.cityofdenton.com/dataset/43e2cf3a-e8d4-4efa-9dae-4adf45b3defc/resource/6b17d3ae-761a-4c81-be74-3a11b3d2b62c/download/43a1d9e8-9255-4b7e-b36b-347fc9d55618texasplaces.geojson')
                st.session_state.Boundries = cities.loc[cities['name'] =='Denton']

        if 'DB_Main' not in st.session_state:
                st.session_state.DB_Main = gpd.read_file(r'Data\Urban_SDK\SDK_Mobility.shp')

        if 'TXDOT' not in st.session_state:
                st.session_state.TXDOT = pd.read_csv(r'Data\TXDOT\TXDOT.csv', header=0 )
                st.session_state.TXDOT['geometry'] = st.session_state.TXDOT['geometry'].apply(wkt.loads)
                st.session_state.TXDOT = gpd.GeoDataFrame (st.session_state.TXDOT, geometry= 'geometry', crs= 2276 )

# Sidebar
st.sidebar.markdown("Map Layers")

selected_layers = []

with st.sidebar:
    check1 = st.checkbox('DB_Main')
    check2 = st.checkbox('TXDOT')
    check3 = st.checkbox('Land Use')
    check4 = st.checkbox('DTCA')
    check5 = st.checkbox('population')
    check6 = st.checkbox('Trucks Route')
    check7 = st.checkbox('Flood layer')
    check8 = st.checkbox('Crash Heat Map')    

if check1:
        selected_layers.append('DB_Main')
        
if check2:
        selected_layers.append ('TXDOT')

if check3:
        selected_layers.append('Land Use')
        
if check4:
        selected_layers.append ('DTCA')

if check5:
        selected_layers.append('population')
        
if check6:
        selected_layers.append ('Trucks Route')

if check7:
        selected_layers.append ('Flood layer')

if check8:
        selected_layers.append ('Crash')


# Plot section
with st.form('Explore Map'):
    map_b = st.form_submit_button('Draw Map', use_container_width = True)

    m = st.session_state.Boundries.explore(name = 'City Boundry')


    if 'DB_Main' in selected_layers:
        st.session_state.DB_Main.explore(m = m, 
        scheme="naturalbreaks",  
        legend=True, 
        tooltip=False, 
        name="Main") 

    if 'TXDOT' in selected_layers:
        st.session_state.TXDOT.explore(
        m=m, 
        color="red",
        marker_kwds=dict(radius=5, fill=True), 
        tooltip=False, 
        name="TXDOT") 

    if 'Land Use' in selected_layers:
        st.session_state.Land_use.explore( m=m, color="green", name="Land Use")  

    if 'population' in selected_layers:
        st.session_state.Popu.explore( m=m, column="POP100", name="Population")  

    if 'DTCA' in selected_layers:
        st.session_state.DTCA.explore( m=m, color="black", name="DTCA") 

    if 'Flood layer' in selected_layers:
        st.session_state.Flood.explore( m=m, column = 'ZONE_SUBTY' , name="Flood" ) 

    if 'Trucks Route' in selected_layers:
        st.session_state.Trucks.explore( m=m, color="purple", name="Trucks") 


# Heat map prep
    file = r'C:\Eastern\DTSC_691\Project\Source_Data\TxDOT_Crash_Data\my_list.csv'
    TXDOT = pd.read_csv(file, header=0)
    TXDOT = TXDOT[TXDOT.Longitude != 'No Data']
    trans = Transformer.from_crs("epsg:4326", "epsg:2276", always_xy=True)
    TXDOT['coord'] = ''
    for i in TXDOT.index:
        TXDOT.at[i, 'coord'] = trans.transform(TXDOT['Longitude'][i], TXDOT['Latitude'][i])
    from folium.plugins import HeatMap
    points = st.session_state.TXDOT['Crash ID'].copy()
    locations = list(zip(TXDOT["Latitude"], TXDOT['Longitude']))
    if 'Crash' in selected_layers:
        HeatMap(locations, name= 'Crash').add_to(m )

    # Base map and layer control:
    folium.TileLayer("CartoDB positron", show=False).add_to(m)  
    folium.LayerControl('topleft').add_to(m)  

    
    # Plot map
    st_folium( m ,  width = 800 , height = 600)

###############################################################################################
