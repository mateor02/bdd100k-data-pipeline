from models.clip import TimeOfDay, Weather, Scene, Clip
import polars as pl
from pydantic import ValidationError
import logging
from utils.s3 import read_parquet_from_s3, upload_parquet_to_s3_sync
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def validate():
    s3 = boto3.Session().client("s3")
    bucket = os.getenv("S3_BUCKET_NAME")
    clean = []
    quarantine = []
    clips_df = read_parquet_from_s3(s3, bucket, "processed/clips/clips.parquet")
    for row in clips_df.iter_rows(named=True):
        try:
            Clip(**row)
            clean.append(row)
            logger.info("Row passed validation")
        except ValidationError as err:
            quarantine.append(row)
            logger.warning(f"Row: {row['name']} failed validation: {err.errors()}")
    logger.info(
        f"Clips that passed validation: {len(clean)} | Clips that didn't pass validation: {len(quarantine)}"
    )

    clean_attributes, quarantine_attributes = pl.DataFrame(clean), pl.DataFrame(
        quarantine
    )

    upload_parquet_to_s3_sync(
        s3, clean_attributes, bucket, "validated/clean/clips.parquet"
    )
    upload_parquet_to_s3_sync(
        s3, quarantine_attributes, bucket, "validated/quarantine/clips.parquet"
    )
    return clean_attributes, quarantine_attributes


if __name__ == "__main__":
    import time

    start = time.time()
    validate()
    elapsed = time.time() - start
    logger.info(f"Validation completed in {elapsed:.2f}s")
