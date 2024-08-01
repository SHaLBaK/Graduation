
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
st.subheader ('Fill the street name, From and To boxes to generate your Map')


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

if 'TXDOT' not in st.session_state:
        st.session_state.TXDOT = 1

# Setting the streets types appriviations
abb_dict = {'Alley ': 'ALY','Avenue ': 'AVE','Boulevard ':'BLVD','Causeway ':'CSWY','Center ':'CTR','Circle ':'CIR',
            'Court ':'CT','Cove ':'CV','Crossing ':'XING','Drive ':'DR','Expressway ':'EXPY','Extension ':'EXT',
            'Freeway ':'FWY','Grove ':'GRV','Highway ':'HWY','Hollow ':'HOLW','Junction ':'JCT','Lane ':'LN',
            'Motorway ':'MTWY','Overpass ':'OPAS','Park ':'PARK','Parkway ':'PKWY','Place ':'PL','Plaza ':'PLZ',
            'Point ':'PT','Road ':'RD','Route ':'RTE','Skyway ':'SKWY','Square ':'SQ','Street ':'ST','Terrace ':'TER',
            'Trail ':'TRL','Way ':'WAY'}

#S###########################################<LOAD DATA>############################################
# file = r'C:\Eastern\DTSC_691\Project\Output\Urban_SDK\SDK_Updated.shp'
# Urban_SDK_updated = gpd.read_file( file )
# Urban_SDK_updated.to_crs(crs = "epsg:2276" , inplace=True)
import time
with st.spinner("Loading Data ... "):

        file = r'C:\Eastern\DTSC_691\Project\Output\Urban_SDK\Urban_SDK_int.shp'
        Urban_SDK_int = gpd.read_file( file )
        Urban_SDK_int.to_crs(crs = "epsg:2276" , inplace=True)


        # Loading the Integrated output from previous process
        Final_db_o = pd.read_csv(r'C:\Eastern\DTSC_691\Project\Output\Final\Final_beforeFlood.csv', low_memory=False , header=0)

        Final_db_o['geometry'] = Final_db_o['geometry'].apply(wkt.loads)

        Final_db_o = gpd.GeoDataFrame (Final_db_o, geometry= 'geometry', crs= 2276 )

        Final_db = Final_db_o[['road_segment_id', 'road_segment_length', 'ST_NAME_sd_',
       'speed_category', 'funclass_name', 'ST_TYPE', 'direction','OWNER_F7', 
       'EX_CLASS', 'FUT_CLASS', 'CONTEXT', 'SPEED', 'BIKE', 'PARKING', 'JURIS',
       'LANES','STATUS','Crash ID', 'Contributing Factors', 'Crash Date',
       'Crash Month', 'Crash Total Injury Count', 'Day of Week', 'Hour of Day',
       'Intersecting Street Name', 'Number of Lanes', 'Road Class',
       'Roadway Type','Distance', 'Transparen', 'Designatio','POP100', 'HU100',
       'route_desc', 'route_type','Sidewalk_I_F6', 'FunCL_F6','SW_Type', 'SW_Materia',
       'From', 'To', 'To_2', 'To_3', 'To_4','geometry']]

#E###########################################<LOAD DATA>############################################

f, g = st.columns( [2, 1 ])

#S###########################################<Values reset>############################
def on_click():
    st.session_state.ST_NAME = ''
    st.session_state.FROM = ''
    st.session_state.TO = ''
#E###########################################<Values reset>############################

#S###########################################<Function Find intersection>############################
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


with st.form('Interactive Map'):
        d, j, e = st.columns ([40 ,1, 15])
        with d:
                a, b , c = st.columns( [1,1,1] )

                with a:
                        st.session_state.ST_NAME = st.text_input('Street Name:', st.session_state.ST_NAME)
                with b:
                        st.session_state.FROM = st.text_input('From:', st.session_state.FROM)
                with c:
                        st.session_state.TO = st.text_input('To:', st.session_state.TO)              
                
                # Clear Button
                map_b = st.form_submit_button('Draw Map', use_container_width = True)
                map_b2 = st.form_submit_button('Clear Names', use_container_width = True, on_click=on_click)

                #Urban_SDK_updated = st.session_state.DB_Main
                # Function Find street segment and plot
                name1 = st.session_state.ST_NAME
                from1 = st.session_state.FROM
                to1 = st.session_state.TO
                Urban_filter1 =  Urban_SDK_int[Urban_SDK_int['ST_NAME_le' ].str.contains ( name1 , case = False)  | 
                        Urban_SDK_int['ST_NAME_ri'].str.contains ( name1 , case = False) ]
                Urban_filter2      =  Urban_filter1 [ Urban_filter1['ST_NAME_ri'].str.contains ( from1 , case = False) |
                        Urban_filter1['ST_NAME_ri'].str.contains ( to1 , case = False)   |
                        Urban_filter1['ST_NAME_le'].str.contains ( from1 , case = False)  |
                        Urban_filter1['ST_NAME_le'].str.contains ( to1 , case = False)      ] 
                partial = Final_db[Final_db['ST_NAME_sd_'].str.contains ( name1 , case = False)]
                p_from = partial[ partial ['From'].str.contains (from1, case =False) |
                        partial ['To'  ].str.contains (from1, case =False) |
                        partial ['To_2'].str.contains (from1, case =False) |
                        partial ['To_3'].str.contains (from1, case =False) |
                        partial ['To_4'].str.contains (from1, case =False) ]
                p_to   = partial[ partial ['From'].str.contains (to1, case =False) |
                        partial ['To'  ].str.contains (to1, case =False) |
                        partial ['To_2'].str.contains (to1, case =False) |
                        partial ['To_3'].str.contains (to1, case =False) |
                        partial ['To_4'].str.contains (to1, case =False) ]               
                line_df = pd.concat ( [ find_intersections ( Urban_filter2 ,p_from ).drop_duplicates('intersection_geom')['intersection_geom'] ,
                                        find_intersections (Urban_filter2 , p_to ).drop_duplicates('intersection_geom') ['intersection_geom']]   )
                line_df.drop_duplicates(inplace=True)

                buff = partial
                if not p_from.empty and not p_to.empty:
                        if  len (line_df) > 1:

                                l1 = LineString ( line_df )
                                line1 = gpd.GeoSeries( [ l1 ], crs = 2276)
                                buff = (line1.centroid).buffer ( (line1).length / 2  )
                else:
                        st.markdown("""
                        <style> .big-font { font-size:30px !important; } </style> """, unsafe_allow_html=True)
                        st.markdown(
                                '<p class="big-font"> Streets dont intersect or incorrect name !</p>', unsafe_allow_html=True)
                
                out1 = partial.clip (buff)
                output_df = out1.drop_duplicates('road_segment_id')              
                        
                st.session_state.output_df = output_df


                
                
        #E###########################################<Plot>############################
                        


        #E###########################################<Input and intersection>############################


        #S###########################################<Metrics>############################

                with e:
                        if not output_df.empty:
                                
                                        options = st.multiselect(
                                        "Select Features to show Metrics:", output_df.columns
                                        , ['ST_NAME_sd_' , 'funclass_name' , 'Designatio' , 'JURIS', 'LANES' , 'road_segment_length', 'FUT_CLASS'], max_selections = 7 )                    

                                        Default_Selection = st.checkbox("Default Selection")

                                        if Default_Selection:
                                                options = ['ST_NAME_sd_' , 'funclass_name' , 'Designatio' , 'JURIS', 'LANES' , 'road_segment_length', 'FUT_CLASS']
                                
                                
                        if map_b:
                                for i in options:
                                        if i == 'road_segment_length':
                                                st.metric( i ,  f'{ round (output_df[ i ].sum(), 2) } Miles' )
                                                continue
                                        if not output_df[i].empty:
                                                st.metric( i ,  output_df[ i ].mode()[0]  )
                

                #S###########################################<Plot>############################
                if not output_df.empty:
                         if map_b:

                                st_folium(st.session_state.output_df.explore ( name = 'Test_output' , legend = True, tooltip=options , popup =options ),
                                        width = 1000 , height = 600, zoom= 17)
                else:
                                st.markdown("""
                                <style> .big-font { font-size:30px !important; } </style> """, unsafe_allow_html=True)

                                st.markdown('<p class="big-font">Please check street names and try again !</p>', unsafe_allow_html=True)




        if map_b:
        #E###########################################<Metrics>############################
                st.divider()
        #E###########################################<Dataframe>############################
                st.dataframe( output_df[options] ,use_container_width = True)
        #E###########################################<Dataframe>############################
#Final_db.columns

# END ALL


