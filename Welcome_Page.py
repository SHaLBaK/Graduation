# Packages
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt

# Page Config
st.set_page_config(layout="wide", page_title='Pages')
st.markdown("""<style> section[data-testid="stSidebar"][aria-expanded="true"]{min-width: 100px;max-width: 250px; display: inline; } </style>""", unsafe_allow_html=True)
# Uncomment this below to activate the sidebar hide
# st.markdown("""
#    <style>
#        section[data-testid="stSidebar"][aria-expanded="true"]{
#            display: none;
#        }
#    </style>
#    """, unsafe_allow_html=True)

# Title
st.title("Mobility Plan Database Integration")
st.subheader("By: Mohammad Shalbak")
st.divider()

st.navigation([st.Page("0_About.py"), st.Page("2_Crash Map.py") ])

# Session state var and DB's:
with st.spinner("Loading Data ... "):
        if 'st_map' not in st.session_state:
                st.session_state.st_map = 0

        if 'output_df' not in st.session_state:
                st.session_state.output_df = 1

        if 'ST_NAME' not in st.session_state:
                st.session_state.ST_NAME = 'Panhandle'

        if 'FROM' not in st.session_state:
                st.session_state.FROM = 'Malone'

        if 'TO' not in st.session_state:
                st.session_state.TO = 'Denton'

        if 'email2' not in st.session_state:
            st.session_state['email2'] = 'no_email'

                # Session state var:
        if 'st_map' not in st.session_state:
                st.session_state.st_map = 0

        if 'output_df' not in st.session_state:
                st.session_state.output_df = 1

        if 'ST_NAME' not in st.session_state:
                st.session_state.ST_NAME = 'eagle'

        if 'FROM' not in st.session_state:
                st.session_state.FROM = 'fulton'

        if 'TO' not in st.session_state:
                st.session_state.TO = 'Welch'

        if 'Intersection_points' not in st.session_state:     
                        Intersection_points = gpd.read_file( r'Data/Urban_SDK/Intersection_points.shp' )
                        Intersection_points.to_crs(crs = "epsg:2276" , inplace=True)
                        st.session_state.Intersection_points = Intersection_points

        if 'Final_db' not in st.session_state:    
                        # Loading the Integrated output from previous process
                        Final_db_o = pd.read_csv(r'Data/Final/Final.csv', header=0 , low_memory = False)
                        Final_db_o['geometry'] = Final_db_o['geometry'].apply(wkt.loads)
                        Final_db = gpd.GeoDataFrame (Final_db_o, geometry= 'geometry', crs= 2276 )
                        st.session_state.Final_db = Final_db
        if 'TXDOT' not in st.session_state:
                st.session_state.TXDOT = pd.read_csv(r'Data/TXDOT/TXDOT.csv', header=0 )
                st.session_state.TXDOT['geometry'] = st.session_state.TXDOT['geometry'].apply(wkt.loads)
                st.session_state.TXDOT = gpd.GeoDataFrame (st.session_state.TXDOT, geometry= 'geometry', crs= 2276 )


#E###########################################<EMAIL CHECK>############################################
st.markdown("""
    <style> .big-font { font-size:20px ; } </style> """, unsafe_allow_html=True)
st.markdown('<p class="big-font"> Enter Email address and press ENTER </p>', unsafe_allow_html=True)

with st.form('Email'):
        email = st.text_input(' ', label_visibility = 'hidden',placeholder ='Type your email here'  )
        Enter = st.form_submit_button('Enter', use_container_width = False , type='primary' )


st.divider()

if email:
    if "cityofdenton.com" in str(email.lower()):

        st.subheader('Welcome, Utilize the sidebar on the left to navigate to the desired page.') #displayed when the button is clicked

        st.markdown("""
        <style> section[data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 100px;
        max-width: 250px; display: inline; } </style>
                    """, unsafe_allow_html=True)

        st.session_state.email2 = email

st.image('https://www.cityofdenton.com/ImageRepository/Document?documentID=5247' , width=600)

