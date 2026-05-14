import streamlit as st
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()

@st.cache_resource
def get_connection():
    engine = create_engine(
        f"awsathena+rest://:@athena.{os.getenv('AWS_REGION')}.amazonaws.com/bdd100k_dbt"
        f"?s3_staging_dir=s3://{os.getenv('S3_BUCKET_NAME')}/athena-results/"
    )
    return engine

@st.cache_data
def get_dataset_distribution(_conn):
    df = pd.read_sql("SELECT * FROM fct_dataset_distribution", _conn)
    return df


