import streamlit as st
import time
import numpy as np
# Basic Python Data Manipulation libraries
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import os

# Visualization libraries
import matplotlib.pyplot as plt
import missingno
import seaborn as sns
from pandas.plotting import scatter_matrix
import folium
#from tabulate import tabulate


# Geospatial libraries
import geopandas as gpd
import contextily as cx
from pyproj import CRS, Transformer
from shapely import wkt
from shapely.geometry import Point, LineString, multilinestring 
import momepy
st.set_page_config(page_title="Plotting Demo")

st.markdown(" Plotting Demo")
st.sidebar.header(" Plotting Demo")
st.write(
    """Fill the street name, From and To boxes to generate your Map""")


st.write('username: ', st.session_state.email2)

a, b, c = st.columns( 3 )

with a:
    ST_NAME = st.text_input('Street Name:', 'Eagle')

with b:
    FROM = st.text_input('From:', 'Carroll')

with c:
    TO = st.text_input('TO:', 'Welch')

# with b:
#     st.selectbox('boo', [2020,2021,2022,2023])

# Start
# ----------------------------------------------------------------- #


# Load the Data
file = r'C:\Eastern\DTSC_691\Project\Output\Urban_SDK\SDK_Updated.shp'

# Since our source data is Geospatial data we will use Geopanda to read the file.
Urban_SDK_updated = gpd.read_file( file )


Urban_SDK_updated.to_crs(crs = "epsg:2276" , inplace=True)

st.title('Counter Example')
if 'count' not in st.session_state:
    st.session_state.count = 0


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
    final_gdf = sj.reset_index()
    # Drop intermediate fields
    drops = ['geom_left', 'geom_right', 'index_right', 'index']
    final_gdf = final_gdf.drop(drops, axis=1)
    return final_gdf


# might not be needed # Using direction to create two buffer DF 
mask =  [ direc in ['N' , 'NE', 'NW'] for direc in Urban_SDK_updated['direction'] ]
Urban_N = Urban_SDK_updated[mask]

mask =  [ direc in ['W' , 'E'] for direc in Urban_SDK_updated['direction'] ]
Urban_E = Urban_SDK_updated[mask]

# Extend the N & E DF's
Urban_N_EX =  momepy.extend_lines(Urban_N, tolerance=20 , target= Urban_N.buffer(14),  extension= 10)
Urban_E_EX =  momepy.extend_lines(Urban_E, tolerance=20 , target= Urban_E.buffer(14),  extension= 10)

Urban_SDK_int = find_intersections (Urban_N_EX , Urban_E_EX)
Urban_SDK_int = Urban_SDK_int [['intersection_geom' , 'ST_NAME_left' , 'ST_NAME_right']]


name1 = ST_NAME
from1 = FROM
to1 = TO

st.session_state.count += 1
st.write( st.session_state.count ,' from before plot' )

Urban_filter1 =  Urban_SDK_int[Urban_SDK_int['ST_NAME_left' ].str.contains ( name1 , case = False)  | 
            Urban_SDK_int['ST_NAME_right'].str.contains ( name1 , case = False) ]
Urban_filter2      =  Urban_filter1 [ Urban_filter1['ST_NAME_right'].str.contains ( from1 , case = False) |
            Urban_filter1['ST_NAME_right'].str.contains ( to1 , case = False)   |
            Urban_filter1['ST_NAME_left'].str.contains ( from1 , case = False)  |
            Urban_filter1['ST_NAME_left'].str.contains ( to1 , case = False)      ] 
partial = Urban_SDK_updated[Urban_SDK_updated['ST_NAME'].str.contains ( name1 , case = False)]
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
l1 = LineString ( line_df )
line1 = gpd.GeoSeries( [ l1 ], crs = 2276)
buff = (line1.centroid).buffer ( (line1).length / 2  )
output_df = partial.clip (buff)
#output_df.explore()
from streamlit_folium import st_folium
map = folium.Map()

#if st.button('Map it !'):

st_map = st_folium(output_df.explore( name = 'Test_output' , legend = True),
        width = 800 , height = 500) 

st.session_state.count += 1
st.write( st.session_state.count ,' from plot' )

st.write ("""
          Test""")
          









# ----------------------------------------------------------------- #
# End
# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)

# for i in range(1, 101):
#     new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#     status_text.text("%i%% Complete" % i)
#     chart.add_rows(new_rows)
#     progress_bar.progress(i)
#     last_rows = new_rows
#     time.sleep(0.05)

# progress_bar.empty()

# # Streamlit widgets automatically run the script from top to bottom. Since
# # this button is not connected to any other logic, it just causes a plain
# # rerun.
# st.button("Re-run")



