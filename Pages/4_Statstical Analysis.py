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
st.title('Crash Counts Statistical page')
st.subheader ('Select a feature from the menu below:')


#E###########################################<Metrics>############################

TXDOT = st.session_state.TXDOT.drop('geometry', axis=1).drop_duplicates('Crash ID')
st.divider()
with st.form('analysis'):
        d,  e = st.columns ([3 ,1])
        with d:
                feature = st.selectbox('Select feature to show count stats' ,
                               ('Day of Wee', 'Hour of Da', 'Crash Tota','Contributi','Road Class',
                                 'Speed Limi', 'Surface Co', 'Weather Co', 'Person Gen' ) )
        with e:
                feature_sec = st.selectbox('Select feature to show count stats' ,
                               (feature,'Day of Wee', 'Hour of Da', 'Crash Tota','Contributi','Road Class',
                                 'Speed Limi', 'Surface Co', 'Weather Co', 'Person Gen' ) , key ='dfsdfsdfsdfs')
        ana = st.form_submit_button('Show count stats', use_container_width = True)

        with st.container (height= 600 , border=True):
                fig, ax = plt.subplots(figsize=(12 , 6))
                plot = sns.countplot( x = TXDOT[feature], stat='count',hue= TXDOT[feature_sec],
                palette="viridis", legend=True ).tick_params(axis='x', rotation=30)
                st.pyplot(fig)
        st.dataframe( TXDOT.groupby([feature]).count().reset_index(),use_container_width = True , height= 500)
        

        
