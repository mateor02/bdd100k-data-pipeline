from io import BytesIO
import polars as pl


async def upload_parquet_to_s3_async(s3, df, bucket, key):
    buffer = BytesIO()
    df.write_parquet(buffer)
    buffer.seek(0)
    await s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def upload_parquet_to_s3_sync(s3, df, bucket, key):
    buffer = BytesIO()
    df.write_parquet(buffer)
    buffer.seek(0)
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def read_parquet_from_s3(s3, bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()
    buffer = BytesIO(data)
    df = pl.read_parquet(buffer)

    return df
