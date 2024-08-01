# Web Library
import streamlit as st
# Page Config
st.set_page_config(layout="wide", page_title='Pages')
#st.sidebar.title('Select a page from the above menu:')

# with st.spinner("Loading Data ... "):

#         # Basic Python Data Manipulation libraries
#         import numpy as np
#         import pandas as pd
#         import math
#         import os

#         # Visualization libraries
#         import matplotlib.pyplot as plt
#         import missingno
#         import seaborn as sns
#         from pandas.plotting import scatter_matrix
#         import folium
#         from streamlit_folium import st_folium
#         from streamlit_folium import folium_static

#         # Geospatial libraries
import geopandas as gpd
#         import contextily as cx
#         from pyproj import CRS, Transformer
#         from shapely import wkt
#         from shapely.geometry import Point, LineString, multilinestring 
#         import momepy





# Session state var:
if 'st_map' not in st.session_state:
        st.session_state.st_map = 0

if 'output_df' not in st.session_state:
        st.session_state.output_df = 1

if 'ST_NAME' not in st.session_state:
        st.session_state.ST_NAME = 'Panhandle'

if 'FROM' not in st.session_state:
        st.session_state.FROM = 'Carroll'

if 'TO' not in st.session_state:
        st.session_state.TO = 'Malone'



if 'email2' not in st.session_state:
    st.session_state['email2'] = 'no_email'

# Unmark this below to activate the sidebar hide
# st.markdown("""
#    <style>
#        section[data-testid="stSidebar"][aria-expanded="true"]{
#            display: none;
#        }
#    </style>
#    """, unsafe_allow_html=True)


st.title("Mobility Plan Batabase Integration")
st.subheader("By: Mohammad Shalbak")
st.divider()

#S###########################################<DB's Initiation>############################################
#S###########################################<LOAD DATA>############################################

with st.spinner("Loading Data ... "):
        if 'boundry' not in st.session_state:
        # Getting the city boundries:
                cities = gpd.read_file('https://data.cityofdenton.com/dataset/43e2cf3a-e8d4-4efa-9dae-4adf45b3defc/resource/6b17d3ae-761a-4c81-be74-3a11b3d2b62c/download/43a1d9e8-9255-4b7e-b36b-347fc9d55618texasplaces.geojson')
                st.session_state.Boundries = cities.loc[cities['name'] =='Denton']

        if 'DB_Main' not in st.session_state:
                st.session_state.DB_Main = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Urban_SDK\SDK_Mobility.shp')

        if 'Urban_SDK_int' not in st.session_state:
                st.session_state.Urban_SDK_int = gpd.read_file( r'C:\Eastern\DTSC_691\Project\Output\Urban_SDK\Urban_SDK_int.shp' )
                st.session_state.Urban_SDK_int.to_crs(crs = "epsg:2276" , inplace=True)

        if 'TXDOT' not in st.session_state:
                st.session_state.TXDOT = gpd.read_file (r'C:\Eastern\DTSC_691\Project\Output\TXDOT\TXDOT_Updated.shp')

        if 'Mobility_current' not in st.session_state:
                st.session_state.Mobility_current = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Mobility_Shape\Mobility.shp'  )

        if 'Land_use' not in st.session_state:
                st.session_state.Land_use = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Land_use\Land_use.shp'  )

        if 'Popu' not in st.session_state:
                st.session_state.Popu = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Popu\Popu.shp'  )

        if 'DTCA' not in st.session_state:
                st.session_state.DTCA = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\DTCA\DTCA.shp'  )

        if 'Sidewalk' not in st.session_state:
                st.session_state.Sidewalk = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Sidewalk\Sidewalk.shp'  )

        if 'Ramps' not in st.session_state:
                st.session_state.Ramps = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Ramps\Ramps.shp'  )

        if 'Flood' not in st.session_state:
                st.session_state.Flood = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Flood\Flood.shp'  )
                #st.session_state.Flood = st.session_state.Flood.clip (Boundries)

        if 'Trucks' not in st.session_state:
                st.session_state.Trucks = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Trucks\Trucks.shp'  )

        if 'Speed' not in st.session_state:
                st.session_state.Speed = gpd.read_file(r'C:\Eastern\DTSC_691\Project\Output\Speed\Speed.shp'  )



#E###########################################<LOAD DATA>############################################


st.markdown("""
    <style> .big-font { font-size:20px ; } </style> """, unsafe_allow_html=True)
st.markdown('<p class="big-font"> Enter Email address and press ENTER </p>', unsafe_allow_html=True)
email = st.text_input(' ', label_visibility = 'hidden',placeholder ='Type your email here'  )
st.divider()

if email:
    if "cityofdenton.com" in str(email.lower()):

        st.subheader('Welcome, Utilize the sidebar on the left to navigate to the desired page.') #displayed when the button is clicked

        st.markdown("""
        <style> section[data-testid="stSidebar"][aria-expanded="true"]{ display: inline; } </style>
                    """, unsafe_allow_html=True)

        st.session_state.email2 = email


st.image('https://www.cityofdenton.com/ImageRepository/Document?documentID=5247')

