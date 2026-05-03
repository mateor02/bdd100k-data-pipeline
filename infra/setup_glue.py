import boto3
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger(__name__)

glue = boto3.client("glue", region_name=os.getenv("AWS_REGION"))

try:
    response = glue.create_database(
        DatabaseInput={
            'Name': 'bdd100k_labels_db',
            'Description': 'Database for validated bdd100k labeled data'
        }
    )
except glue.exceptions.AlreadyExistsException:
    logger.info("Database already exists, skipping creation")

try:    
    response = glue.create_crawler(
        Name='bdd100k_crawler',
        Role='GlueS3CrawlerRole',
        DatabaseName='bdd100k_labels_db',
        Description='Crawler for database',
        Targets={
            'S3Targets' : [
                {
                    'Path': f"s3://{os.getenv('S3_BUCKET_NAME')}/validated/clean/"
                }
            ]
        }
    )
except glue.exceptions.AlreadyExistsException:
    logger.info("Crawler already exists, skipping creation")
    
glue.start_crawler(Name='bdd100k_crawler')
logger.info("Crawler started")