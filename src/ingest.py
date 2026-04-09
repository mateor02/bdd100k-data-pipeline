from dotenv import load_dotenv
import os
import boto3
from boto3.s3.transfer import S3UploadFailedError
from pathlib import Path
import concurrent.futures

load_dotenv()

p = Path("/Users/mateomelgoza/Developer/projects/bdd100k-data-pipeline/data/100k/train")
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))


def local_to_s3(s3_client, file_name, bucket, key):
    try:
        s3_client.upload_file(file_name, bucket, key)
        print(f"Uploaded file {file_name} into bucket {bucket} with key {key}")
    except S3UploadFailedError as err:
        print(f"Couldn't upload file {file_name} to {bucket} with key {key}")
        print(f"\t{err}")


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for file in p.glob("*"):
            executor.submit(
                local_to_s3,
                s3,
                str(file),
                os.getenv("S3_BUCKET_NAME"),
                f"raw/labels/{file.name}",
            )
