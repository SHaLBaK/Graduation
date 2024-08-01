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


st.set_page_config(layout="wide")
st.title('Interactive Crash stats and DataFrame')
st.subheader ('Fill intersection streets names, and Radius Distance')

## Data Source
### TxDOT Crash data
TXDOT = st.session_state.TXDOT
Urban_SDK_int = st.session_state.Urban_SDK_int
Dist = 1



# Since our source data is Geospatial data we will use Geopanda to read the file.
TXDOT = pd.read_csv(r'C:\Eastern\DTSC_691\Project\Source_Data\TxDOT_Crash_Data\my_list.csv', header=0)
TXDOT = TXDOT[TXDOT.Longitude != 'No Data']
# Transfer the coordinates to the porper EPSG: 2276
trans = Transformer.from_crs("epsg:4326", "epsg:2276", always_xy=True)
TXDOT['coord'] = ''
for i in TXDOT.index:
        TXDOT.at[i, 'coord'] = trans.transform(TXDOT['Longitude'][i], TXDOT['Latitude'][i])



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


with st.form('Interactive Map'):
        d, j, e = st.columns ([40 ,1, 15])
        with d:

                a, b , c = st.columns( [1,1,1] )

                with a:
                        st.session_state.ST_NAME = st.text_input('Street Name:', st.session_state.ST_NAME)
                with b:
                        st.session_state.FROM = st.text_input('From:', st.session_state.FROM)
                with c:
                        Dist = st.number_input('Distance:', value=200)
                map_b = st.form_submit_button('Draw Map', use_container_width = True)
                map_b2 = st.form_submit_button('Clear Names', use_container_width = True, on_click=on_click)
                # Function Find street segment and plot
                name1 = st.session_state.ST_NAME
                from1 = st.session_state.FROM
                to1 = st.session_state.TO
                Urban_filter1 =  Urban_SDK_int[Urban_SDK_int['ST_NAME_le' ].str.contains ( name1 , case = False)  | 
                        Urban_SDK_int['ST_NAME_ri'].str.contains ( name1 , case = False) ]
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

                # crashes_buff = gpd.GeoDataFrame (output_df.groupby(['geometry'])['Crash ID'].count().reset_index(), geometry='geometry' , crs = 2276)
                # crash_df = crashes_buff

                if not output_df.empty:
                        # m = output_df.explore(
                        # #column="geometry",  # make choropleth based on "POP2010" column
                        # scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
                        # legend=True,  # show legend
                        # k=10,  # use 10 bins
                        # tooltip=True,  # hide tooltip
                        # #popup=["POP2010", "POP2000"],  # show popup (on-click)
                        # legend_kwds=dict(colorbar=False),  # do not use colorbar
                        # name="Main",  # name of the layer in the map
                        # )

                        m = output_df.explore(
                        # pass the map object
                        color="red",  # use red color on all points
                        marker_kwds=dict(radius=5, fill=True),  # make marker radius 10px with fill
                        #tooltip="Address",  # show "name" column in the tooltip
                        tooltip_kwds=dict(labels=False),  # do not show column label in the tooltip
                        name="Crash Point",  # name of the layer in the map
                        )
                        
                        # Get x and y coordinates for each point
                        locations = list(zip(TXDOT["Latitude"], TXDOT['Longitude']))

                        HeatMap(locations, name="Heat").add_to(m)

                        folium.TileLayer("CartoDB positron", show=False).add_to(m)  # use folium to add alternative tiles

                        folium.LayerControl().add_to(m)  # use folium to add layer control

                        st_folium( m , width = 950 , height = 600, zoom= 17)    # show map
                                


                                #     st_folium(output_df.drop_duplicates('Crash ID').explore ( marker_type=  folium.Circle (radius = 10*5 ,
                                #     fill = True) ,color = 'red' , fill = True , opacity = len(crash_df.drop_duplicates('Crash ID')) *10,
                                #     style_kwds=dict( fillOpacity = len(crash_df.drop_duplicates('Crash ID'))/20  ) ),
                                #     width = 1000 , height = 600, zoom= 17)
                else:
                                st.markdown("""
                                <style>
                                .big-font {
                                font-size:30px !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)

                                st.markdown('<p class="big-font">Please check street names and try again !</p>', unsafe_allow_html=True)

#S###########################################<Metrics>############################

                with e:
                        #if not output_df.empty:
                                
                        options = st.multiselect(
                        "Select Features to show Metrics:", output_df.columns
                        , ['ST_NAME_l1' , 'Crash ID_l1' ,'Day of Wee_l1'], max_selections = 7 )                   
                        button1 = st.form_submit_button('Default selection', disabled=False, )       
                                
                                
                        if map_b:
                                for i in options:
                                        if i == 'Length':
                                                st.metric( i ,  f'{ round (output_df[ i ].sum(), 2) } Miles' )
                                        if not output_df[i].empty:
                                                st.metric( i ,  output_df[ i ].mode()[0]  )
                                output_df['Contributi_l1']

#S###########################################<Metrics>############################
                # if not output_df.empty:
                #         output_df.drop_duplicates('Crash ID', inplace = True )
                #         st.subheader('Metrics :')
                #         col1, col2 = st.columns(2)
                #         output_df['Contributi']
                #         for i in options:
                #                 st.metric( i ,  output_df[ i ].mode()[0]  )
                # col1.metric("Speed Category",  output_df['speed_cate'].mode()[0]  )
                # col1.metric('Classification', output_df.iloc[0][4] )
                # col2.metric('Parking', 'Parking:', f'+{output_df.iloc[0][4]}' )
                # col2.metric('Length', f'{round ( output_df['road_seg_1'].astype (float).sum() ,2 )} Mile' ) #.iloc [0][1])#.sum() )
                # st.divider()
                # st.subheader('Other Metrics (if available):')      
#E###########################################<Metrics>############################
st.divider()


st.dataframe( output_df[options],use_container_width = True , height= 500)

st.divider()
# f, g = st.columns( [2, 1 ])
# with f:
#     with st.container (height= 800 , border=True):
#         fig, ax = plt.subplots(figsize=(6.4 , 4.8))
#         plot = sns.barplot( TXDOT['Day of Wee'].value_counts(),
#         palette="rocket", legend=False ).tick_params(axis='x', rotation=30)
#         st.pyplot(fig)



# st.session_state.TXDOT = TXDOT