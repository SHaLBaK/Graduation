
# Basic Python Data Manipulation libraries
import numpy as np
import pandas as pd
import math
import os

# Visualization libraries
import matplotlib.pyplot as plt
import missingno
import seaborn as sns
from pandas.plotting import scatter_matrix
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static

# Geospatial libraries
import geopandas as gpd
import contextily as cx
from pyproj import CRS, Transformer
from shapely import wkt
from shapely.geometry import Point, LineString, multilinestring 
import momepy

# Web Library
import streamlit as st

# Page Config
st.set_page_config(layout="wide")
st.title('Interactive Map Plot and DataFrame')
st.subheader ('Fill in the Street name, From and To Fields to generate your Map')
st.markdown("""<style> section[data-testid="stSidebar"][aria-expanded="true"]{min-width: 100px;max-width: 250px; display: inline; } </style>""", unsafe_allow_html=True)

# Setting the streets types appriviations var
abb_dict = {'Alley ': 'ALY','Avenue ': 'AVE','Boulevard ':'BLVD','Causeway ':'CSWY','Center ':'CTR','Circle ':'CIR',
            'Court ':'CT','Cove ':'CV','Crossing ':'XING','Drive ':'DR','Expressway ':'EXPY','Extension ':'EXT',
            'Freeway ':'FWY','Grove ':'GRV','Highway ':'HWY','Hollow ':'HOLW','Junction ':'JCT','Lane ':'LN',
            'Motorway ':'MTWY','Overpass ':'OPAS','Park ':'PARK','Parkway ':'PKWY','Place ':'PL','Plaza ':'PLZ',
            'Point ':'PT','Road ':'RD','Route ':'RTE','Skyway ':'SKWY','Square ':'SQ','Street ':'ST','Terrace ':'TER',
            'Trail ':'TRL','Way ':'WAY'}

# Setting the features to column dict:
features_dict = {'ST_NAME_sd_' : 'Street name',
        'road_segment_length' : 'Total Length',
        'speed_category' : 'Speed Limit',
        'funclass_name': 'Street Classification',
        'OWNER_F7': 'Street Ownership',
        'CONTEXT': 'Living Context',
        'BIKE': 'Bike' ,
        'PARKING':'Parking',
        'JURIS': 'Juristriction',
        'SCHZONE':'School Zone',
        'LANES': 'Number of Lanes',
        'Crash ID':'Number of crashes',
        'Designatio':'Designation',
        'POP100': 'Population',
        'HU100': 'House numbers',
        'FNODE1_1': 'Truck route',
        'Sidewalk_I_F6':'Sidewalk'}
        
# Setting the interface selection names and order:
Selections = ['Street name','Total Length','Street Classification','Street Ownership','Juristriction',
                      'Living Context','Speed Limit','Number of crashes','Bike','Parking','School Zone',
                      'Number of Lanes','Designation','Population','House numbers','Truck route','Sidewalk']
options = []

#S###########################################<Values reset>############################
f, g = st.columns( [2, 1 ])

def on_click():
    st.session_state.ST_NAME = ''
    st.session_state.FROM = ''
    st.session_state.TO = ''
#E###########################################<Values reset>############################

#S###########################################<Function Find intersection>##############
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
    #sj = sj[sj.index != sj.index_right]

    # Extract the intersecting geometry
    sj['intersection_geom'] = sj['geom_left'].intersection(sj['geom_right'])

    # Reset the geometry (remember to set the CRS correctly!)
    sj.set_geometry('intersection_geom',  inplace=True, crs=gdf.crs)

    # Drop duplicate geometries
    #final_gdf = sj.drop_duplicates(subset=['geometry']).reset_index()
    final_gdf = sj.reset_index()

    # Drop intermediate fields
    drops = ['geom_left', 'geom_right', 'index'] #, 'index_right'
    final_gdf = final_gdf.drop(drops, axis=1)

    return final_gdf
#E###########################################<Function Find intersection>############################




#S###########################################<Input and intersection>############################

with st.form('Interactive Segment Map'):
        d, j, e = st.columns ([40 ,1, 15])
        with d:
                # User input section:
                a, b , c = st.columns( [1,1,1] )

                with a:
                        st.session_state.ST_NAME = st.text_input('Street Name:', st.session_state.ST_NAME)
                with b:
                        st.session_state.FROM = st.text_input('From:', st.session_state.FROM)
                with c:
                        st.session_state.TO = st.text_input('To:', st.session_state.TO)              
                
                # Clear and submit Buttons
                map_b = st.form_submit_button('Draw Map', use_container_width = True)
                map_b2 = st.form_submit_button('Clear Names', use_container_width = True, on_click=on_click)

                # Filter database based on use input and find street segment:
                name1 = st.session_state.ST_NAME
                from1 = st.session_state.FROM
                to1 = st.session_state.TO

                Filter1 =  st.session_state.Intersection_points[st.session_state.Intersection_points['ST_NAME_le' ].str.contains ( name1 , case = False)  | 
                        st.session_state.Intersection_points['ST_NAME_ri'].str.contains ( name1 , case = False) ]
                Filter2      =  Filter1 [ Filter1['ST_NAME_ri'].str.contains ( from1 , case = False) |
                        Filter1['ST_NAME_ri'].str.contains ( to1 , case = False)   |
                        Filter1['ST_NAME_le'].str.contains ( from1 , case = False)  |
                        Filter1['ST_NAME_le'].str.contains ( to1 , case = False)      ] 
                Filtered_DB = st.session_state.Final_db[st.session_state.Final_db['ST_NAME_sd_'].str.contains ( name1 , case = False)]
                Filtered_from = Filtered_DB[ Filtered_DB ['From'].str.contains (from1, case =False) |
                        Filtered_DB ['To'  ].str.contains (from1, case =False) |
                        Filtered_DB ['To_2'].str.contains (from1, case =False) |
                        Filtered_DB ['To_3'].str.contains (from1, case =False) |
                        Filtered_DB ['To_4'].str.contains (from1, case =False) ]
                Filtered_to   = Filtered_DB[ Filtered_DB ['From'].str.contains (to1, case =False) |
                        Filtered_DB ['To'  ].str.contains (to1, case =False) |
                        Filtered_DB ['To_2'].str.contains (to1, case =False) |
                        Filtered_DB ['To_3'].str.contains (to1, case =False) |
                        Filtered_DB ['To_4'].str.contains (to1, case =False) ]               
                
                # Create a line from user input intersection points:
                line_df = pd.concat ( [ find_intersections ( Filter2 ,Filtered_from ).drop_duplicates('intersection_geom')['intersection_geom'] ,
                                        find_intersections (Filter2 , Filtered_to ).drop_duplicates('intersection_geom') ['intersection_geom']]   )
                line_df.drop_duplicates(inplace=True)

                # create a buffer for the line that equals to the line length / 2 
                buff = Filtered_DB
                if not Filtered_from.empty and not Filtered_to.empty:
                        if  len (line_df) > 1:

                                l1 = LineString ( line_df )
                                line1 = gpd.GeoSeries( [ l1 ], crs = 2276)
                                buff = (line1.centroid).buffer ( (line1).length / 2  )
                else:
                        st.markdown("""
                        <style> .big-font { font-size:30px !important; } </style> """, unsafe_allow_html=True)
                        st.markdown(
                                '<p class="big-font"> Streets dont intersect or incorrect name !</p>', unsafe_allow_html=True)
                
                # Clip the filtered DB to the intersection of interest:
                out1 = Filtered_DB.clip (buff)
                output_df = out1.drop_duplicates('road_segment_id')              
                st.session_state.output_df = output_df

                

        #S###########################################<Metrics>############################
                # Setting up metricts section and values:
                with e:
                        if not output_df.empty:
                                
                                options_n = st.multiselect(
                                        "Select Features to show Metrics:", Selections
                                        , ['Street name','Total Length','Street Classification','Street Ownership'], max_selections = 7 )                    

                                Default_Selection = st.checkbox("Default Selection")

                                if Default_Selection:
                                                options_n = []
                                                options = ['ST_NAME_sd_' , 'funclass_name' , 'Designatio' , 'JURIS', 'LANES' , 'road_segment_length']
                                
                        if map_b:
                                for i in features_dict:
                                        if features_dict.get(i) in options_n:
                                                options.append (i) 

                                for i in options:
                                        
                                        if i == 'road_segment_length':
                                                st.metric( 'Total Length' ,  f'{ round (output_df[ i ].sum(), 2) } Miles' )
                                                continue
                                        
                                        if i == 'POP100':
                                                st.metric( 'Surrounding Population' ,  output_df[ i ].sum() )
                                                continue

                                        if i == 'Crash ID':
                                                st.metric( 'Number of Crashes' ,  output_df[ i ].drop_duplicates().count() )
                                                continue

                                        if i in ['SCHZONE','Crash ID', 'FNODE1_1', 'Sidewalk_I_F6'] :
                                                ref = features_dict.get(i)     
                                                if output_df[ i ].mode().empty:
                                                        st.metric( ref ,  'No' )
                                                        continue
                                                else:
                                                        st.metric( ref ,  'Yes' )
                                                        continue   

                                        if not output_df[i].empty:
                                                ref = features_dict.get(i)
                                                st.metric( ref ,  output_df[ i ].mode()[0]  )              

        #S###########################################<Plot>############################
                if not output_df.empty:
                         if map_b:

                                st_folium(st.session_state.output_df.explore ( name = 'Test_output' , legend = True, tooltip=options , popup =options ),
                                        width = 1000 , height = 600, zoom= 15)
                else:
                                st.markdown("""
                                <style> .big-font { font-size:30px !important; } </style> """, unsafe_allow_html=True)

                                st.markdown('<p class="big-font">Please check street names and try again !</p>', unsafe_allow_html=True)

        if map_b:
        #E###########################################<Plot>############################

                st.divider()
        #E###########################################<Dataframe>######################
                st.dataframe( output_df[options] ,use_container_width = True)
        #E###########################################<Dataframe>######################


# END ALL


