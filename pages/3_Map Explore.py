import folium.map
import pandas as pd
import matplotlib.pyplot as plt
import folium
import os
import geopandas as gpd

import streamlit as st

st.set_page_config(layout="wide")


st.title('Interactive Explore Map')
st.subheader ('Use sidebar checkbox to select layer to show')


import folium

from streamlit_folium import st_folium

st.sidebar.markdown("Map Layers")
#selected_layers = ['DB_Main','TXDOT', 'Crash','Land Use','population' , 'DTCA', 'Flood layer' , 'Trucks Route']
selected_layers = []
        #layer_name
        #for layer_name in ['DB_Main','TXDOT', 'Crash','Land Use','population' , 'DTCA', 'Flood layer' , 'Trucks Route']

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

with st.form('Interactive Explore Map'):
    map_b = st.form_submit_button('Draw Map', use_container_width = True)

    m = st.session_state.Boundries.explore(name = 'City Boundry')

    if 'DB_Main' in selected_layers:
        st.session_state.DB_Main.explore(m = m, 
        #column="geometry",  # make choropleth based on "POP2010" column
        scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
        legend=True,  # show legend
        k=10,  # use 10 bins
        tooltip=False,  # hide tooltip
        #popup=["POP2010", "POP2000"],  # show popup (on-click)
        legend_kwds=dict(colorbar=False),
        tooltip_kwds=dict(labels=True),  # do not show column label in the tooltip
        name="Main") # name of the layer in the map

    if 'TXDOT' in selected_layers:
        st.session_state.TXDOT.explore(
        m=m,  # pass the map object
        color="red",  # use red color on all points
        marker_kwds=dict(radius=5, fill=True),  # make marker radius 10px with fill
        tooltip=False,  # show "name" column in the tooltip
        tooltip_kwds=dict(labels=False),  # do not show column label in the tooltip
        name="TXDOT")  # name of the layer in the map

    if 'Land Use' in selected_layers:
        st.session_state.Land_use.explore( m=m, color="green", name="Land Use")  

    if 'population' in selected_layers:
        st.session_state.Popu.explore( m=m, column="POP100", name="Population")  

    if 'DTCA' in selected_layers:
        st.session_state.DTCA.explore( m=m, color="black", name="DTCA") 

    if 'Flood layer' in selected_layers:
        st.session_state.Flood.explore( m=m,  column ='FLD_ZONE' , name="Flood") 

    if 'Trucks Route' in selected_layers:
        st.session_state.Trucks.explore( m=m, color="41bc03", name="Trucks") 

    from pyproj import CRS, Transformer

    file = r'data/TxDOT_Crash_Data/my_list.csv'

    # Since our source data is Geospatial data we will use Geopanda to read the file.
    TXDOT = pd.read_csv(file, header=0)
    TXDOT = TXDOT[TXDOT.Longitude != 'No Data']
    # Transfer the coordinates to the porper EPSG: 2276
    trans = Transformer.from_crs("epsg:4326", "epsg:2276", always_xy=True)

    TXDOT['coord'] = ''

    for i in TXDOT.index:
        TXDOT.at[i, 'coord'] = trans.transform(TXDOT['Longitude'][i], TXDOT['Latitude'][i])

    from folium.plugins import HeatMap

    points = st.session_state.TXDOT['Crash ID'].copy()
    # Get x and y coordinates for each point

    locations = list(zip(TXDOT["Latitude"], TXDOT['Longitude']))

    if 'Crash' in selected_layers:
        HeatMap(locations, name= 'Crash').add_to(m )

    folium.TileLayer("CartoDB positron", show=False).add_to(m)  # use folium to add alternative tiles

    folium.LayerControl().add_to(m)  # use folium to add layer control

    st_folium( m , width = 1380 , height = 900)    # show map


#             ) , use_container_width=True
#         )
#choropleth.add_to(map)

###############################################################################################
