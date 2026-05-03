import boto3
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

athena = boto3.client("athena", region_name=os.getenv("AWS_REGION"))

try:
    response = athena.create_work_group(
        Name='bdd100k_athena',
        Configuration={
            'ResultConfiguration': {
                'OutputLocation': f"s3://{os.getenv('S3_BUCKET_NAME')}/athena-results/"
            }
        }
    )
except athena.exceptions.InvalidRequestExceptoin:
    logger.info("Athena client already exists, skipping creation")
    
