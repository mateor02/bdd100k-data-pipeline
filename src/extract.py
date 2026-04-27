from dotenv import load_dotenv
import os
import asyncio
import aioboto3
import polars as pl
from botocore.exceptions import ClientError
import json
from io import BytesIO
from utils.s3 import upload_parquet_to_s3_async

load_dotenv()


async def extract_s3_object(s3, semaphore, bucket, s3_key):
    clip_dict = None
    objects_list = []
    segmentation_list = []
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
                if "box2d" in obj:
                    objects_list.append(
                        {
                            "name": name,
                            "category": obj["category"],
                            "id": obj["id"],
                            "occluded": obj["attributes"]["occluded"],
                            "truncated": obj["attributes"]["truncated"],
                            "trafficLightColor": obj["attributes"]["trafficLightColor"],
                            "x1": obj["box2d"]["x1"],
                            "y1": obj["box2d"]["y1"],
                            "x2": obj["box2d"]["x2"],
                            "y2": obj["box2d"]["y2"],
                        }
                    )
                elif "poly2d" in obj:
                    segmentation_list.append(
                        {
                            "name": name,
                            "category": obj["category"],
                            "id": obj["id"],
                            "direction": obj["attributes"].get("direction"),
                            "style": obj["attributes"].get("style"),
                            "poly2d": json.dumps(obj["poly2d"]),
                        }
                    )

    except ClientError as err:
        print(f"Couldn't access page")
        print(f"\t{err}")

    return clip_dict, objects_list, segmentation_list


async def main():
    session = aioboto3.Session()
    semaphore = asyncio.Semaphore(250)
    bucket = os.getenv("S3_BUCKET_NAME")
    tasks = []

    async with session.client("s3") as s3:
        paginator = s3.get_paginator("list_objects_v2")
        limit = int(os.getenv("MAX_ITEMS", 0))
        pagination_config = {"MaxItems": limit} if limit else {}
        pages = paginator.paginate(
            Bucket=bucket, Prefix="raw/labels", PaginationConfig=pagination_config
        )
        async for page in pages:
            contents = page.get("Contents", [])
            for key in contents:
                tasks.append(extract_s3_object(s3, semaphore, bucket, key["Key"]))
        results = await asyncio.gather(*tasks, return_exceptions=True)

        clips = []
        objects = []
        segmentations = []
        for i, result in enumerate(results):
            if result is not None and not isinstance(result, Exception):
                clip, objs, seg = result
                clips.append(clip)
                objects.extend(objs)
                segmentations.extend(seg)
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1} files...")
        clips_df = pl.DataFrame(clips)
        objects_df = pl.DataFrame(objects)
        segmentations_df = pl.DataFrame(segmentations)

        await upload_parquet_to_s3_async(
            s3, clips_df, bucket, "processed/clips/clips.parquet"
        )
        await upload_parquet_to_s3_async(
            s3, objects_df, bucket, "processed/objects/objects"
        )
        await upload_parquet_to_s3_async(
            s3,
            segmentations_df,
            bucket,
            "processed/segmentations/segmentations.parquet",
        )

        print(
            f"Extracted {len(clips)} clips, {len(objects)} objects, {len(segmentations)} segmentations"
        )

    return clips_df, objects_df, segmentations_df


if __name__ == "__main__":
    import time

    start = time.time()
    asyncio.run(main())
    elapsed = time.time() - start
    print(f"Took {int(elapsed // 60)}m {elapsed % 60:.2f}s")
