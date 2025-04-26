import streamlit as st
import pandas as pd
import numpy as np
import datetime
import pydeck as pdk
import plotly.express as px

st.set_page_config(layout="wide")
st.title('Uber pickups in NYC')

# Load data
DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data = load_data(10000)

# Show raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# Date input
d = st.date_input("Please select date", datetime.date(2014, 9, 1))
filtered_data = data[data[DATE_COLUMN].dt.date == d]

# Chart using numpy histogram (แบบเดิม)
st.subheader('Number of pickups by hour (st.bar_chart)')
hist_values = np.histogram(filtered_data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
st.bar_chart(hist_values)

# Chart using Plotly (แบบใหม่)
st.subheader('Hourly pickup trend (Plotly Line Chart)')

# เตรียมข้อมูลเป็นแบบต่อเนื่อง รายชั่วโมงในวันนั้น
plot_df = filtered_data.copy()
plot_df['Hour'] = plot_df[DATE_COLUMN].dt.hour

# นับจำนวน pickup ต่อชั่วโมง
hourly_counts = plot_df.groupby('Hour').size().reset_index(name='Pickups')

# วาดกราฟเส้นด้วย Plotly
fig = px.line(hourly_counts, x='Hour', y='Pickups', markers=True,
              title='Pickup Trend by Hour (Plotly Line Chart)')
st.plotly_chart(fig)

# Selectbox for hour
hour = st.selectbox('Select hour to view pickup locations', list(range(24)), index=17)
hourly_data = filtered_data[filtered_data[DATE_COLUMN].dt.hour == hour]

# Map 2D
st.subheader('Map of all pickups at %s:00' % hour)
st.map(hourly_data)

# PyDeck 3D map
st.subheader(f'3D map of pickups at {hour}:00')
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=40.7128,
        longitude=-74.0060,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=hourly_data,
           get_position='[lon, lat]',
           radius=100,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
    ],
))

# Button counter
if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button('Click to increase counter'):
    st.session_state.count += 1

st.write(f"This page has run {st.session_state.count} times.")





