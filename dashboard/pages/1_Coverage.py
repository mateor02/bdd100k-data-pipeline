import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from queries import get_connection, get_dataset_distribution
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.header("Dataset Coverage Analysis", divider=True)

df = get_dataset_distribution(get_connection())
selected_values = df['weather'].unique()

with st.sidebar: 
    selected = st.selectbox(
        label="Select different categories to compare",
        options=(("time_of_day", "weather"), ("weather", "scene_type"), ("time_of_day", "scene_type")),
        format_func=lambda x: f"{x[0]} × {x[1]}"
    )
    
    weather_options = st.multiselect(
        label="Filter by weather",
        options=selected_values,
        default=selected_values
    )
filtered_df = df[df['weather'].isin(weather_options)]
index_col, columns_col = selected

table = pd.pivot_table(filtered_df, values='clip_count', index=index_col, columns=columns_col, aggfunc='sum', fill_value=0)


st.subheader("Dataset distribution heat map")
st.plotly_chart(px.imshow(table, color_continuous_scale='Viridis'))





fig1 = px.bar(filtered_df, x='weather', y='clip_count', orientation ='v', hover_data=['pct_of_dataset'])
fig2 = px.bar(filtered_df, x='time_of_day', y='clip_count', orientation='v', hover_data=['pct_of_dataset'])
fig3 = px.bar(filtered_df, x='scene_type', y='clip_count', orientation='v', hover_data=['pct_of_dataset'])


st.subheader("Distribution by weather")
st.plotly_chart(fig1)
    
st.subheader("Distribution by time_of_day")
st.plotly_chart(fig2)

st.subheader("Distribution by scene_type")
st.plotly_chart(fig3)
