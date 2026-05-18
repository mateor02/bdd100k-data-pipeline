import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
from queries import get_connection, get_clip_summary

# Page config — sets browser tab title, icon, and wide layout
st.set_page_config(
    page_title="BDD100K Labeling Pipeline",
    page_icon="🚗",
    layout="wide",
)

# ---------- Hero ----------
st.title("🚗 BDD100K Labeling Pipeline Dashboard")
st.markdown(
    """
    An end-to-end **data engineering pipeline simulating an FSD labeling ops workflow** —
    ingesting 70,000 dashcam clip annotations from Berkeley's BDD100K dataset and
    surfacing coverage, density, and quality insights for autonomous vehicle perception teams.
    """
)

st.divider()

# ---------- Dataset at a glance ----------
st.subheader("Dataset at a Glance")

df = get_clip_summary(get_connection())

col1, col2, col3 = st.columns(3)
col1.metric("Total Clips", f"{len(df):,}")
col2.metric("Total Object Annotations", f"{int(df['total_objects'].sum()):,}")
col3.metric("Total Segmentations", f"{int(df['total_segmentations'].sum()):,}")

st.divider()

# ---------- What's in this dashboard ----------
st.subheader("What's in this dashboard")
st.markdown(
    """
    **📊 Coverage Analysis** — Distribution of clips across weather, time-of-day, and scene-type
    conditions. Identifies over- and under-represented combinations to inform labeling
    prioritization.

    **🔍 Clip Explorer** — Per-clip exploration with filtering by environmental conditions,
    annotation density distributions, and a dedicated **Vulnerable Road Users** section
    surfacing pedestrian and cyclist coverage — the highest-priority edge cases in FSD safety.
    """
)

st.divider()

# ---------- Technical stack ----------
st.subheader("Technical Stack")
st.markdown(
    """
    - **Ingestion & Transformation**: Python (Polars, Pydantic v2, asyncio)
    - **Cloud Storage & Compute**: AWS S3, Glue Catalog, Athena
    - **Modeling Layer**: dbt-athena (5 models, 54 tests passing)
    - **Dashboard**: Streamlit + Plotly, querying Athena via SQLAlchemy/pyathena
    - **Tooling**: uv for dependency management, planned: Airflow + Docker
    """
)

st.divider()

# ---------- Footer ----------
st.caption("Built by Mateo Melgoza · [GitHub](https://github.com/mateor02/bdd100k-data-pipeline)")