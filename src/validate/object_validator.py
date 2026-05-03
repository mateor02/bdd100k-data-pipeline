from models.object import Object
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


def validate_objects():
    s3 = boto3.Session().client("s3")
    bucket = os.getenv("S3_BUCKET_NAME")
    objects_df = read_parquet_from_s3(s3, bucket, "processed/objects/objects.parquet")
    clean_objects, quarantine_objects = validator(objects_df, Object)

    upload_parquet_to_s3_sync(
        s3, clean_objects, bucket, "validated/clean/objects/objects.parquet"
    )

    upload_parquet_to_s3_sync(
        s3, quarantine_objects, bucket, "validated/quarantine/objects/objects.parquet"
    )


if __name__ == "__main__":
    validate_objects()
