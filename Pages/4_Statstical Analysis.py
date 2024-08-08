import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(layout="wide")
st.title('Crash Counts Statistical page')
st.subheader ('Select a feature from the menu below:')
st.markdown("""<style> section[data-testid="stSidebar"][aria-expanded="true"]{min-width: 100px;max-width: 250px; display: inline; } </style>""", unsafe_allow_html=True)

#E###########################################<Stats>############################

TXDOT = st.session_state.TXDOT.drop('geometry', axis=1).drop_duplicates('Crash ID')
TXDOT['Hour of Day'] = TXDOT['Hour of Day'].astype('category')
st.divider()
with st.form('analysis'):
        d,  e = st.columns ([3 ,1])
        with d:
                feature = st.selectbox('Select feature to show count stats' ,
                               ('Day of Week', 'Hour of Day', 'Crash Total Injury Count','Contributing Factors','Road Class',
                                 'Speed Limit', 'Surface Condition', 'Weather Condition', 'Person Gender' ) )
        with e:
                feature_sec = st.selectbox('Select feature to show count stats' ,
                               (feature,'Day of Week', 'Hour of Day', 'Crash Total Injury Count','Contributing Factors','Road Class',
                                 'Speed Limit', 'Surface Condition', 'Weather Condition', 'Person Gender' ) , key ='dfsdfsdfsdfs')
        ana = st.form_submit_button('Show count stats', use_container_width = True)

        with st.container (height= 720,  border=True):
                a, b = st.columns(2)
                with a:
                        st.write ('Count graph')
                        fig, ax = plt.subplots(figsize=(10 , 8))
                        plot = sns.countplot( x = TXDOT[feature], stat='count',hue= TXDOT[feature_sec],
                        order= TXDOT[feature].value_counts().index.to_list (),
                        palette="viridis", legend=True )
                        plot.tick_params(axis='x', rotation=30)

                        for container in plot.containers:
                                plot.bar_label(container)
                        st.pyplot(fig)
                        TXDOT[feature].value_counts() 
                with b:
                        st.write ('Box graph (Day of Week)')
                        fig1, ax = plt.subplots(figsize=(10 , 8))
                        sns.boxplot( TXDOT, hue = feature , y= 'Hour of Day',
                                    palette="viridis", legend=False , gap= 0.2 ).tick_params(axis='x', rotation=30)
                        st.pyplot(fig1)
        
        st.dataframe( TXDOT.groupby([feature], observed=False).count().reset_index(),use_container_width = True , height= 500 )







