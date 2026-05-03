from models.clip import Clip
import logging
from utils.s3 import read_parquet_from_s3, upload_parquet_to_s3_sync
import boto3
import os
from dotenv import load_dotenv
from utils.validation import validator

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def validate_clips():
    s3 = boto3.Session().client("s3")
    bucket = os.getenv("S3_BUCKET_NAME")
    clips_df = read_parquet_from_s3(s3, bucket, "processed/clips/clips.parquet")
    clean_attributes, quarantine_attributes = validator(clips_df, Clip)

    upload_parquet_to_s3_sync(
        s3, clean_attributes, bucket, "validated/clean/clips/clips.parquet"
    )
    upload_parquet_to_s3_sync(
        s3, quarantine_attributes, bucket, "validated/quarantine/clips/clips.parquet"
    )


if __name__ == "__main__":
    validate_clips()
