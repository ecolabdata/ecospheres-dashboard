import os
import shutil
import subprocess
import tempfile

from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError


def connect_to_s3():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="nl-ams",
            endpoint_url="https://s3.nl-ams.scw.cloud",
        )
        print("Connected to S3 bucket")
        return s3
    except NoCredentialsError:
        print("Invalid credentials")
        return None


def list_bucket_contents(bucket_name, s3_client):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        print(f"Contents of {bucket_name}:")
        for obj in response.get("Contents", []):
            print(obj["Key"])
    except Exception as e:
        print(f"An error occurred while listing bucket contents: {str(e)}")


def upload_file(local_file_path, bucket_name, object_key, s3_client):
    try:
        # Upload the file
        s3_client.upload_file(local_file_path, bucket_name, object_key)
        print("File uploaded successfully")
    except Exception as e:
        print(f"An error occurred during upload: {str(e)}")


def create_database_dump(dsn):
    try:
        # Create a temporary directory for the dump file
        temp_dir = tempfile.mkdtemp()
        dump_file_path = Path(temp_dir) / "database_dump.sql"

        # Execute pg_dump command
        command = f"pg_dump '{dsn}' > {dump_file_path}"
        subprocess.run(command, shell=True, check=True)

        return temp_dir, dump_file_path
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during database dump creation: {str(e)}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None, None

def cleanup_temp_directory(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up successfully")
    except Exception as e:
        print(f"Failed to clean up temporary directory: {str(e)}")


# Initialize S3 client
s3_client = connect_to_s3()
if s3_client is None:
    exit(1)

bucket_name = "ecospheres-backups"

temp_dir, dump_file_path = create_database_dump(os.getenv("DATABASE_URL"))

if dump_file_path:
    object_key = "backups/database_dump.sql"
    upload_success = upload_file(dump_file_path, bucket_name, object_key, s3_client)
    if upload_success:
        cleanup_temp_directory(temp_dir)
        list_bucket_contents(bucket_name, s3_client)  # List contents again to verify the upload
    else:
        print("Upload failed. Cleaning up temporary directory...")
        cleanup_temp_directory(temp_dir)
else:
    print("Failed to create database dump")
