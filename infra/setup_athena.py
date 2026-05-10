import boto3
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_workgroup_if_not_exists(athena, workgroup_name: str, output_location: str) -> None:

    try:
        athena.create_work_group(
            Name=workgroup_name,
            Configuration={"ResultConfiguration": {"OutputLocation": output_location}},
        )
        logger.info("Workgroup created: %s", workgroup_name)

    except athena.exceptions.InvalidRequestException as err:
        if "already exists" in str(err):
            logger.info("Workgroup already exists, skipping creation")
        else:
            raise


def main():
    athena = boto3.client("athena", region_name=os.getenv("AWS_REGION"))
    name = "bdd100k_athena"
    output_location = f"s3://{os.getenv('S3_BUCKET_NAME')}/athena-results/"

    create_workgroup_if_not_exists(athena, name, output_location)


if __name__ == "__main__":
    main()
