import boto3
import os
from dotenv import load_dotenv
import logging
import time
from botocore.exceptions import ClientError

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger(__name__)


def create_database_if_not_exists(glue, name: str, database_description: str) -> None:
    try:
        glue.create_database(
            DatabaseInput={"Name": name, "Description": database_description}
        )
        logger.info("Database created: %s", name)

    except glue.exceptions.AlreadyExistsException:
        logger.info("Database already exists, skipping creation")


def create_crawler_if_not_exists(glue, name: str, role: str, database: str, crawler_description: str, s3_path: str) -> None:
    try:
        response = glue.create_crawler(
            Name=name,
            Role=role,
            DatabaseName=database,
            Description=crawler_description,
            Targets={"S3Targets": [{"Path": s3_path}]},
        )
    except glue.exceptions.AlreadyExistsException:
        logger.info("Crawler already exists, skipping creation")


def start_crawler_and_wait(glue, name: str, poll_interval: int = 15) -> None:
    glue.start_crawler(Name=name)
    logger.info("Crawler started, waiting for completion...")

    try:
        while True:
            response = glue.get_crawler(Name=name)
            state = response["Crawler"]["State"]

            if state == "READY":
                logger.info("Crawler completed successfully")
                break

            logger.info("Crawler state: %s, waiting...", state)
            time.sleep(poll_interval)

    except ClientError as err:
        logger.error(
            "Couldn't get crawler %s. Here's why: %s: %s",
            name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise


def main():
    glue = boto3.client("glue", region_name=os.getenv("AWS_REGION"))
    database_name = "bdd100k_labels_db"
    crawler_role = "GlueS3CrawlerRole"
    crawler_name = "bdd100k_crawler"
    s3_path = f"s3://{os.getenv('S3_BUCKET_NAME')}/validated/clean/"

    create_database_if_not_exists(
        glue=glue,
        name=database_name,
        database_description="Database for validated bdd100k labeled data",
    )

    create_crawler_if_not_exists(
        glue=glue,
        name=crawler_name,
        role=crawler_role,
        database=database_name,
        crawler_description="Crawler for database",
        s3_path=s3_path,
    )

    start_crawler_and_wait(glue, crawler_name)


if __name__ == "__main__":
    main()
