from dotenv import load_dotenv
import os
import asyncio
import aioboto3
import polars as pl
from botocore.exceptions import ClientError
import json
import pathlib

load_dotenv()


async def extract_s3_object(s3, semaphore, bucket, s3_key):
    objects = None
    try:
        async with semaphore:
            response = await s3.get_object(Bucket=bucket, Key=s3_key)
            data = json.loads(await response["Body"].read())
            name = data["name"]
            attributes = data["attributes"]
            objects = {
                "name": name,
                "timeofday": attributes["timeofday"],
                "weather": attributes["weather"],
                "scene": attributes["scene"],
            }
            print(f"Extracted file {name} from {bucket}")

    except ClientError as err:
        print(f"Couldn't access page")
        print(f"\t{err}")

    return objects


async def main():
    session = aioboto3.Session()
    semaphore = asyncio.Semaphore(250)
    bucket = os.getenv("S3_BUCKET_NAME")
    tasks = []

    async with session.client("s3") as s3:
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix="raw/labels")
        async for page in pages:
            contents = page.get("Contents", [])
            for key in contents:
                tasks.append(extract_s3_object(s3, semaphore, bucket, key["Key"]))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    df = pl.DataFrame(
        [r for r in results if r is not None and not isinstance(r, Exception)]
    )
    path = pathlib.Path("data/labels.parquet")
    df.write_parquet(path)
    return df

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(main())
    elapsed = time.time() - start
    print(f"Took {int(elapsed // 60)}m {elapsed % 60:.2f}s")