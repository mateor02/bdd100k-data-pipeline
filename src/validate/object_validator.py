from models.object import TrafficLightColor, Category, Object
import polars as pl
from pydantic import ValidationError
import logging
from utils.s3 import read_parquet_from_s3, upload_parquet_to_s3_sync
import boto3
import os
from dotenv import load_dotenv

load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def 