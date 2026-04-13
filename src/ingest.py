from dotenv import load_dotenv
import os
import asyncio
import aioboto3
from pathlib import Path
from botocore.exceptions import ClientError

load_dotenv()

async def files_to_s3(session, semaphore, bucket, file_path, key):
    async with semaphore:
        async with session.client("s3") as s3:
            try:
                await s3.head_object(Bucket=bucket, Key=key)
                print(f"Key:{key} already exists")
            except ClientError as err:
                if err.response['Error']['Code'] == "404":
                    await s3.upload_file(Filename=file_path, Bucket=bucket, Key=key)
                    print(f"File: {key} uploaded successfully")
                else:
                    print(f"Unexpected error for {key}: {err}")
                    raise err
        
async def main():
    semaphore = asyncio.Semaphore(100)
    bucket = os.getenv("S3_BUCKET_NAME")
    local_path = Path("/Users/mateomelgoza/Developer/projects/bdd100k-data-pipeline/data/100k/train")
    session = aioboto3.Session()
    tasks = []
    
    for file in local_path.glob("*"):
        key = f"raw/labels/{file.name}"
        tasks.append(files_to_s3(session, semaphore, bucket, str(file), key))
    await asyncio.gather(*tasks, return_exceptions=True)
    
if __name__ == "__main__":
    asyncio.run(main())