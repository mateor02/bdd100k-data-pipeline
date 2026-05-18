import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from queries import get_connection, get_dataset_distribution
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.header("Dataset Coverage Analysis", divider=True)

st.markdown(
    """
    This page analyzes how clips are distributed across environmental conditions —
    weather, time of day, and scene type. Use the sidebar to switch the heatmap's
    cross-tabulation dimensions or filter by weather; all charts respond.

    Coverage gaps revealed here inform labeling prioritization: a perception model
    trained on imbalanced data performs unpredictably in under-represented conditions.
    """
)

df = get_dataset_distribution(get_connection())
weather_options = df['weather'].unique()

with st.sidebar: 
    selected = st.selectbox(
        label="Select different categories to compare",
        options=(("time_of_day", "weather"), ("weather", "scene_type"), ("time_of_day", "scene_type")),
        format_func=lambda x: f"{x[0]} × {x[1]}"
    )
    
    selected_values = st.multiselect(
        label="Filter by weather",
        options=weather_options,
        default=weather_options
    )
filtered_df = df[df['weather'].isin(selected_values)]
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
