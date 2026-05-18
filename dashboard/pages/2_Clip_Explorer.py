import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from queries import get_clip_summary, get_connection
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.header("Clip Explorer", divider=True)

st.markdown(
    """
    Per-clip exploration of all 70,000 annotated clips. Filter by environmental
    conditions in the sidebar; metrics, distributions, and the table all respond.

    Designed to surface annotation density patterns, vulnerable road user (VRU)
    coverage, and outlier clips worth flagging for QA review.
    """
)

df = get_clip_summary(get_connection())

# Unique values for each environmental dimension. These become the
# OPTIONS shown in the sidebar multiselects (not the selected values).
weather_options = df['weather'].unique()
time_options = df['time_of_day'].unique()
scene_options = df['scene_type'].unique()

with st.sidebar:
    # Each multiselect returns a list of the user's currently selected values.
    # Default to all options means the page loads showing everything
    weather_sidebar = st.multiselect(
        label="Select weather type",
        options=weather_options,
        default=weather_options
    )
    
    time_sidebar = st.multiselect(
        label="Select specific time of day",
        options=time_options,
        default=time_options
    )
    
    scene_sidebar = st.multiselect(
        label="Select specific scene type",
        options=scene_options,
        default=scene_options
    )

# Filter the full 70k-row DataFrame down to the rows matching ALL three sidebar selections.
# Each .isin() returns a boolean Series (one True/False per row of df).
# '&' combines them with AND logic: a row survives only if it matches every condition.
# Result has the same columns as df, just fewer rows.
filtered_df = df[
    df['weather'].isin(weather_sidebar)         # row's weather is in user-selected weather
    & df['time_of_day'].isin(time_sidebar)      # AND row's time_of_day is in user_selected times
    & df['scene_type'].isin(scene_sidebar)      # AND row's scene_type is in user-selected scenes
]

is_filtered = len(filtered_df) < len(df)    # Constraint for showing deltas only when user filters certain categories

col1, col2, col3 = st.columns(3)
with col1:
    pct_of_dataset = round(len(filtered_df) / len(df) * 100, 2)
    
    st.metric(
        label="Total Clips", 
        value=len(filtered_df), 
        delta=f"{pct_of_dataset}% of dataset",
        delta_color="off"
    )
with col2:
    filtered_obj_avg = filtered_df['total_objects'].mean() if len(filtered_df) > 0 else 0
    dataset_obj_avg = df['total_objects'].mean()
    delta_obj = round(filtered_obj_avg - dataset_obj_avg, 2) if is_filtered else None
    
    st.metric(
        label="Avg objects per clip", 
        value=round(filtered_obj_avg, 2), 
        delta=delta_obj
    )
with col3:
    filtered_seg_avg = filtered_df['total_segmentations'].mean() if len(filtered_df) > 0 else 0
    dataset_seg_avg = df['total_segmentations'].mean()
    delta_seg = round(filtered_seg_avg - dataset_seg_avg, 2) if is_filtered else None
    
    st.metric(
        label="Avg segmentations per clip",
        value=round(filtered_seg_avg, 2),
        delta=delta_seg
    )
    
st.subheader("Distribution of annotation density per clip")
st.plotly_chart(px.histogram(filtered_df, x = 'total_objects', nbins=20))
st.markdown("Distribution is right-skewed - most clips fall below 25 objects, with a long tail of dense scenes representing busy urban intersections")



st.subheader("Vulnerable Road Users")

clips_with_peds = filtered_df[filtered_df['total_pedestrians'] > 0]

vru_col1, vru_col2, vru_col3, vru_col4 = st.columns(4)
with vru_col1:
    pct_with_pedestrians = (filtered_df['total_pedestrians'] > 0).mean() * 100 if len(filtered_df) > 0 else 0
    st.metric(
        label="Pedestrian Coverage",
        value=f"{round(pct_with_pedestrians, 2)}%",
        help="Percentage of clips in the filtered set containing at least one pedestrian."
    )
with vru_col2:
    avg_pedestrians = clips_with_peds['total_pedestrians'].mean() if len(clips_with_peds) > 0 else 0
    st.metric(
        label="Avg Pedestrians",
        value=f"{round(avg_pedestrians, 1)}",
        help="Average pedestrians per clip where present."
    )
with vru_col3:
    pct_peds_infra = (filtered_df['total_pedestrian_infrastructure'] > 0).mean() * 100 if len(filtered_df) > 0 else 0
    st.metric(
        label="Infrastructure Coverage",
        value=f"{round(pct_peds_infra, 2)}%",
        help="Percentage of clips with pedestrian infrastructure"
    )
with vru_col4:
    pct_cyclists = (filtered_df['total_cyclists'] > 0).mean() * 100 if len(filtered_df) > 0 else 0
    st.metric(
        label="Cyclist Coverage",
        value=f"{round(pct_cyclists, 2)}%",
        help="Percentage of clips with cyclists"
    )


# Reuse the pre-filtered "clips with pedestrians" subset so the histogram
# isn't dominated by the (very tall) zero-pedestrians bar.
st.subheader("Pedestrian count distribution (clips with pedestrians)")
st.plotly_chart(px.histogram(clips_with_peds, x="total_pedestrians", nbins=20))

st.subheader("Top 100 Most Sparsely Labeled Clips (Possible QA Candidates)")
st.dataframe(filtered_df[['clip_id', 
                          'weather', 
                          'time_of_day', 
                          'scene_type', 
                          'total_objects', 
                          'total_pedestrians', 
                          'total_pedestrian_infrastructure',
                          'total_segmentations']]
            .sort_values(by='total_objects', ascending=True)
            .head(100)
)


