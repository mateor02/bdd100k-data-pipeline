from models.segmentation import Segmentation
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


def validate_segmentations():
    s3 = boto3.Session().client("s3")
    bucket = os.getenv("S3_BUCKET_NAME")
    segmentations_df = read_parquet_from_s3(s3, bucket, "processed/segmentations/segmentations.parquet")
    clean_segmentations, quarantine_segmentations = validator(segmentations_df, Segmentation)

    upload_parquet_to_s3_sync(
        s3, clean_segmentations, bucket, "validated/clean/segmentations/segmentations.parquet"
    )

    upload_parquet_to_s3_sync(
        s3, quarantine_segmentations, bucket, "validated/quarantine/segmentations/segmentations.parquet",
    )


if __name__ == "__main__":
    validate_segmentations()
