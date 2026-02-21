
import os
import boto3
from jproperties import Properties

# Mock settings enough to run s3
configs = Properties()
with open('config.properties', 'rb') as config_file:
    configs.load(config_file)

AWS_ACCESS_KEY_ID = configs.get("aws_access_key_id").data
AWS_SECRET_ACCESS_KEY = configs.get("aws_secret_access_key").data
AWS_REGION = configs.get("aws_region").data
AWS_S3_BUCKET = configs.get("aws_s3_bucket").data

print(f"Testing S3 bucket: {AWS_S3_BUCKET} in {AWS_REGION}")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

try:
    s3.put_object(
        Bucket=AWS_S3_BUCKET,
        Key="test_write_magicpic.txt",
        Body=b"test",
        ContentType="text/plain"
    )
    print("Successfully wrote to bucket!")
    s3.delete_object(Bucket=AWS_S3_BUCKET, Key="test_write_magicpic.txt")
    print("Successfully deleted test object!")
except Exception as e:
    print(f"S3 Error: {e}")
