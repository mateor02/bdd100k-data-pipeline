from dotenv import load_dotenv
import os
import asyncio
import aioboto3
import polars as pl
from botocore.exceptions import ClientError
import json
import pathlib

load_dotenv()

valid_categories = [
    "car",
    "truck",
    "bus",
    "person",
    "rider",
    "bicycle",
    "motorcycle",
    "traffic light",
    "traffic sign",
    "train",
]


async def extract_s3_object(s3, semaphore, bucket, s3_key):
    clip_dict = None
    objects_list = []
    try:
        async with semaphore:
            response = await s3.get_object(Bucket=bucket, Key=s3_key)
            data = json.loads(await response["Body"].read())
            name = data["name"]
            attributes = data["attributes"]
            clip_dict = {
                "name": name,
                "timeofday": attributes["timeofday"],
                "weather": attributes["weather"],
                "scene": attributes["scene"],
            }
            for obj in data["frames"][0]["objects"]:
                if obj["category"] in valid_categories:
                    objects_list.append(
                        {
                            "name": name,
                            "category": obj["category"],
                            "occluded": obj["attributes"]["occluded"],
                            "truncated": obj["attributes"]["truncated"],
                        }
                    )

            print(f"Extracted file {name} from {bucket}")

    except ClientError as err:
        print(f"Couldn't access page")
        print(f"\t{err}")

    return clip_dict, objects_list


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

    clips = []
    objects = []
    for result in results:
        if result is not None and not isinstance(result, Exception):
            clip, objs = result
            clips.append(clip)
            objects.extend(objs)
    clips_df = pl.DataFrame(clips)
    objects_df = pl.DataFrame(objects)
    clips_path = pathlib.Path("data/clips.parquet")
    objects_path = pathlib.Path("data/objects.parquet")
    clips_df.write_parquet(clips_path)
    objects_df.write_parquet(objects_path)

    return clips_df, objects_df


if __name__ == "__main__":
    import time

    start = time.time()
    asyncio.run(main())
    elapsed = time.time() - start
    print(f"Took {int(elapsed // 60)}m {elapsed % 60:.2f}s")
