# Packages
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

# Page setup
st.set_page_config(layout="wide")
st.title('Intersection Crash stats and DataFrame')
st.subheader ('Fill intersection streets names, and Radius Distance')
st.markdown("""<style> section[data-testid="stSidebar"][aria-expanded="true"]{min-width: 100px;max-width: 250px; display: inline; } </style>""", unsafe_allow_html=True)


## Data and var.
### TxDOT Crash data
TXDOT = pd.read_csv(r'Data/TxDOT_Crash_Data/my_list (1)_Updated.csv', header=0 )
TXDOT = TXDOT[TXDOT.Longitude != 'No Data']
trans = Transformer.from_crs("epsg:4326", "epsg:2276", always_xy=True)
TXDOT['coord'] = ''
for i in TXDOT.index:
        TXDOT.at[i, 'coord'] = trans.transform(TXDOT['Longitude'][i], TXDOT['Latitude'][i])

Dist = 1

# Other Data
if 'Intersection_points' not in st.session_state:
        st.session_state.Intersection_points = 1
        Intersection_points = gpd.read_file( r'Data/Urban_SDK/Intersection_points.shp' )
        Intersection_points.to_crs(crs = "epsg:2276" , inplace=True)
        Intersection_points = st.session_state.Intersection_points 

features_dic  = {'Crash Total Injury Count_l1': 'Total Injuries', 'Fatal Crash Flag_l1':'Fatality',
       'Contributing Factors_l1' : 'Factors','Day of Week_l1': 'Day',
       'Hour of Day_l1': 'Hour', 'Speed Limit_l1': 'Posted Speed', 'Surface Condition_l1': 'Surface',
       'Weather Condition_l1': 'Weather', 'Charge_l1': 'Charge','Person Age_l1': 'Age', 
       'Person Gender_l1':'Gender'}

Selections = ['Day','Posted Speed','Weather','Fatality','Hour','Total Injuries' ,'Surface','Charge','Age','Gender']
options = []


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

# other Functions
def on_click():
    st.session_state.ST_NAME = ''
    st.session_state.FROM = ''
    st.session_state.TO = ''

def fatality_color(value):
    if value == 1:
        return "black"
    return "red"

# Input section
with st.form('Interactive Map'):
        d, j, e = st.columns ([40 ,1, 15])
        with d:

                a, b , c = st.columns( [1,1,1] )

                with a:
                        st.session_state.ST_NAME = st.text_input('Street Name:', st.session_state.ST_NAME)
                with b:
                        st.session_state.FROM = st.text_input('Intersects:', st.session_state.FROM)
                with c:
                        Dist = st.number_input('Distance:', value=200)
                map_b = st.form_submit_button('Draw Map', use_container_width = True)
                map_b2 = st.form_submit_button('Clear Names', use_container_width = True, on_click=on_click)
                # Function Find street segment and plot
                name1 = st.session_state.ST_NAME
                from1 = st.session_state.FROM
                to1 = st.session_state.TO
                Urban_filter1 =  st.session_state.Intersection_points[st.session_state.Intersection_points['ST_NAME_le' ].str.contains ( name1 , case = False)  | 
                        st.session_state.Intersection_points['ST_NAME_ri'].str.contains ( name1 , case = False) ]
                Urban_filter2 =  Urban_filter1 [ Urban_filter1['ST_NAME_ri'].str.contains ( from1 , case = False) |
                        Urban_filter1['ST_NAME_le'].str.contains ( from1 , case = False) ] 
                
                partial = st.session_state.TXDOT.drop_duplicates('Crash ID').sjoin_nearest(Urban_filter2 , max_distance= Dist )
                
                if  partial.empty :
                        st.markdown("""
                        <style>
                        .big-font {
                        font-size:30px !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown('<p class="big-font">Streets dont intersect or incorrect name !</p>', unsafe_allow_html=True)
                        output_df = partial.sjoin_nearest (st.session_state.TXDOT , how= 'left', max_distance = Dist ,lsuffix='l1', rsuffix='r1')

                else:


                        output_df = partial.sjoin_nearest (st.session_state.TXDOT , how= 'left', max_distance = Dist ,lsuffix='l1', rsuffix='r1')
                        output_df.drop_duplicates('Crash ID_l1', inplace= True)         
                                
                        st.session_state.output_df = output_df


#S###########################################<Metrics>############################
                with e:
                        options_n = st.multiselect(
                                        "Select Features to show Metrics:", Selections
                                        , ['Total Injuries','Day','Posted Speed','Weather'], max_selections = 7 )                    

                        Default_Selection = st.checkbox("Default Selection")

                        if Default_Selection:
                                                options_n = []
                                                options = ['Day of Week_l1', 'Speed Limit_l1','Weather Condition_l1', 'Crash Total Injury Count_l1' ]
                             
                        if map_b:
                                for i in features_dic:
                                        if features_dic.get(i) in options_n:
                                                options.append (i) 
                                        

                                for i in options:
                                        ref = features_dic.get(i)
                                        if not output_df[i].empty:
                                                ref = features_dic.get(i)
                                                st.metric( ref ,  output_df[ i ].mode()[0]  )
                                st.write('Contributing Factors')
                                st.dataframe(output_df['Contributing Factors_l1'].unique())
                        
                        output_df['FC'] = output_df['Fatal Crash Flag_l1'].astype(bool)

                if not output_df.empty:
                        
                        m = output_df.explore( column = 'Fatal Crash Flag_l1',  
                        legend = True,   colorbar = False, 
                        tooltip=options , popup =options,
                        categorical=True, cmap=['black', 'red'],
                        marker_type = folium.CircleMarker (radius=6, fill = True),
                        marker_kwds=dict(radius=4, fill=True),  
                        tooltip_kwds=dict(labels=False),  
                        name="Crash Point",control_scale = True,  
                        )


                        # prep points for Heat map
                        locations = list(zip(TXDOT["Latitude"], TXDOT['Longitude']))

                        HeatMap(locations, name="Heat").add_to(m)

                        folium.TileLayer("CartoDB positron", show=False).add_to(m) 

                        folium.LayerControl('topleft').add_to(m) 

                        st_folium( m , width = 950 , height = 600, zoom= 17 ) 


                else:
                                st.markdown("""
                                <style>
                                .big-font {
                                font-size:30px !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)

                                st.markdown('<p class="big-font">Please check street names and try again !</p>', unsafe_allow_html=True)


#E###########################################<Metrics>############################

st.divider()

# Plot Dataframe
st.dataframe( output_df[options],use_container_width = True , height= 500)

st.divider()
