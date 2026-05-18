import streamlit as st
import os
from sqlalchemy import create_engine
import pandas as pd


@st.cache_resource
def get_connection():
    # Make AWS credentials available to boto3/pyathena via env vars
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS_SECRET_ACCESS_KEY"]
    
    engine = create_engine(
        f"awsathena+rest://:@athena.{st.secrets['AWS_REGION']}.amazonaws.com/bdd100k_dbt"
        f"?s3_staging_dir=s3://{st.secrets['S3_BUCKET_NAME']}/athena-results/"
    )
    return engine

@st.cache_data
def get_dataset_distribution(_conn):
    df = pd.read_sql("SELECT * FROM fct_dataset_distribution", _conn)
    return df

@st.cache_data
def get_clip_summary(_conn):
    df = pd.read_sql("SELECT * FROM fct_clip_summary", _conn)
    return df

