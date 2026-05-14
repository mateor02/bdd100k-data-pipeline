import streamlit as st
from queries import get_connection

st.header("BDD100k Labeling Pipeline Dashboard", divider=True)
st.markdown("- **Streamlit dashboard** querying the dbt marts via Athena — coverage analysis views, per-clip exploration, filtering by environmental attributes")


