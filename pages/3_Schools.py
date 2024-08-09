import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import CRS, Transformer
import geopandas as gpd
import seaborn as sns
from shapely.geometry import Point, LineString, multilinestring 
import folium
from streamlit_folium import st_folium
from pyproj import CRS, Transformer
from folium.plugins import HeatMap
from shapely import wkt


st.set_page_config(layout="wide")
st.title('Schools data')
st.subheader ('Select school name, Feature and Radius Distance')


st.markdown("""<style> section[data-testid="stSidebar"][aria-expanded="true"]{min-width: 100px;max-width: 250px; display: inline; } </style>""", unsafe_allow_html=True)


## Data Source

Schools = gpd.read_file( r'data/Schools/Schools.shp' )
Schools.to_crs(crs = "epsg:2276" , inplace=True)

schools_names = Schools.SCHOOL.to_list()

if 'Sidewalk' not in st.session_state:
                st.session_state.Sidewalk = gpd.read_file(r'data/Sidewalk/Sidewalk.shp'  )

features_dict = {'ST_NAME_sd_' : 'Street name',
                'road_segment_length' : 'Total Length',
                'speed_category' : 'Speed Limit',
                'funclass_name': 'Street Classification',
                'OWNER_F7': 'Street Ownership',
                'CONTEXT': 'Living Context',
                'BIKE_l1': 'Bike' ,
                'PARKING':'Parking',
                'JURIS': 'Juristriction',
                'SCHZONE':'School Zone',
                'LANES': 'Number of Lanes',
                'Crash ID_l1':'Number of crashes',
                'Designatio_l1':'Designation',
                'POP100': 'Population',
                'HU100': 'House numbers',
                'FNODE1_1': 'Truck route',
                'Sidewalk_I_F6_r1':'Sidewalk'}
        
        # Setting the interface selection names and order:
Selections = ['Number of crashes','Bike','Designation','Sidewalk']
options = []
#st.session_state.Final_db.columns
Final_DB_SW = st.session_state.Final_db[['Sidewalk_I_F6','Crash ID', 'BIKE','Designatio','geometry' ]]

# Function to find intersection
# Original Code from Jesse Nestler:
# (https://medium.com/@jesse.b.nestler/how-to-find-geometry-intersections-within-the-same-dataset-using-geopandas-59cd1a5f30f9)

#Intersection with two DF's
def find_intersections(gdf_A: gpd.GeoDataFrame, gdf_B: gpd.GeoDataFrame):
    # Save geometries to another field
    gdf = gdf_A.copy()
    gdf1 = gdf_B.copy()
    
    # Save geometries to another field
    gdf['geom'] = gdf.geometry
    gdf1['geom'] = gdf1.geometry

    # Self join
    sj = gpd.sjoin(gdf, gdf1,
                   how="inner",
                   predicate="intersects",
                   lsuffix="left",
                   rsuffix="right")

    # Remove geometries that intersect themselves
    sj = sj[sj.index != sj.index_right]

    # Extract the intersecting geometry
    sj['intersection_geom'] = sj['geom_left'].intersection(sj['geom_right'])

    # Reset the geometry (remember to set the CRS correctly!)
    sj.set_geometry('intersection_geom',  inplace=True, crs=gdf.crs)

    # Drop duplicate geometries
    #final_gdf = sj.drop_duplicates(subset=['geometry']).reset_index()
    final_gdf = sj.reset_index()

    # Drop intermediate fields
    drops = ['geom_left', 'geom_right', 'index_right', 'index']
    final_gdf = final_gdf.drop(drops, axis=1)

    return final_gdf

# End Function Find intersection


def on_click():
    st.session_state.ST_NAME = ''
    st.session_state.FROM = ''
    st.session_state.TO = ''

def fatality_color(value):  # scalar value defined in 'column'
    if value == 1:
        return "black"
    return "red"

with st.form('School'):
        d, j, e = st.columns ([40 ,1, 15])
        with d:

                a, c = st.columns( [1,1] )

                with a:
                        school_na = st.multiselect(
                                        "Select School", schools_names ,
                                        ['McMath Middle School'], max_selections = 1 )
                with c:
                        Dist = st.number_input('Distance:', value=2000)
                S1 = st.form_submit_button('Find School', use_container_width = True)
                S2 = st.form_submit_button('Clear Names', use_container_width = True, on_click=on_click)
                # Function Find street segment and plot
                buffer = Schools[Schools['SCHOOL'] == school_na[0]].geometry.centroid.buffer (Dist)


                
                partial = Final_DB_SW.drop_duplicates().clip (buffer)
                Sidewalk = st.session_state.Sidewalk.drop_duplicates().clip (buffer)
                
                if  partial.empty :
                        st.markdown("""
                        <style>
                        .big-font {
                        font-size:30px !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown('<p class="big-font">Check the Distance and try again!</p>', unsafe_allow_html=True)
                        output_df = partial.sjoin_nearest (Final_DB_SW , how= 'left', max_distance = Dist ,lsuffix='l1', rsuffix='r1')
                        

                else:


                        output_df = partial.sjoin_nearest (Final_DB_SW , how= 'left', max_distance = Dist ,lsuffix='l1', rsuffix='r1')
                        output_df.drop_duplicates('Crash ID_l1', inplace= True)         
                                
                        st.session_state.output_df = output_df

#S###########################################<Metrics>############################

                with e:
                        #output_df.columns 
                        options_n = st.multiselect(
                                "Select Features to show Metrics:", Selections
                                , ['Sidewalk','Bike' ], max_selections = 7 )        

                        Default_Selection = st.checkbox("Default Selection")

                        if Default_Selection:
                                options_n = ['Sidewalk','Bike']
                                options = ['Crash ID_l1','BIKE_l1' ]
                               
                                
                        if S1:
                                for i in features_dict:
                                        if features_dict.get(i) in options_n:
                                                options.append (i) 

                                for i in options:
                                        if i == 'Crash ID_l1':
                                                st.metric( 'Number of Crashes' ,  output_df[ i ].drop_duplicates().count() )
                                                continue
                                        if i == 'Sidewalk_I_F6_r1':
                                                continue

                                        ref = features_dict.get(i)
                                        if not output_df[i].empty:
                                                ref = features_dict.get(i)
                                                st.metric( ref ,  output_df[ i ].mode()[0]  )

                if not output_df.empty:
                         if S1:
                                m = Schools[Schools['SCHOOL'] == school_na[0]].explore(name = 'School' , color = 'green')
                                Sidewalk.explore( m=m, color="red", name="Sidewalk") 

                                st_folium(m , width = 1000 , height = 600, zoom= 15)
                else:
                                m = Schools[Schools['SCHOOL'] == school_na[0]].explore(name = 'School' , color = 'green')
                                
                                st_folium(m , width = 1000 , height = 600, zoom= 15)

#E###########################################<Metrics>############################

st.divider()

st.dataframe( output_df[options],use_container_width = True , height= 500)

st.divider()
