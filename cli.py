import os
import shutil
import subprocess
import tempfile

from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError

# thoses databases will be backuped and uploaded to S3
DATABASES = {
    "dashboard": os.getenv("DATABASE_URL"),
    "dashboard_backend": os.getenv("DOKKU_POSTGRES_AQUA_URL"),
}
BUCKET_NAME = "ecospheres-backups"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

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
        return True
    except Exception as e:
        print(f"An error occurred during upload: {str(e)}")


def create_database_dump(dsn):
    try:
        # Create a temporary directory for the dump file
        temp_dir = tempfile.mkdtemp()
        dump_file_path = Path(temp_dir) / "database_dump.sql"

        # Execute pg_dump command
        command = f"pg_dump '{dsn}' | gzip > {dump_file_path}"
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


def delete_old_backups(bucket_name, s3_client, days_to_keep=7):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        objects_to_delete = []

        for obj in response.get("Contents", []):
            obj_key = obj["Key"]
            obj_last_modified = obj["LastModified"]

            # Calculate the age of the backup
            obj_age = (datetime.now(obj_last_modified.tzinfo) - obj_last_modified).days

            # If the backup is older than the specified number of days, mark it for deletion
            if obj_age > days_to_keep:
                objects_to_delete.append({"Key": obj_key})

        if objects_to_delete:
            s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": objects_to_delete}
            )
            print(f"Deleted {len(objects_to_delete)} old backups")
        else:
            print("No old backups found to delete")

    except Exception as e:
        print(f"An error occurred while deleting old backups: {str(e)}")


s3_client = connect_to_s3()
if s3_client is None:
    exit(1)


for database_name, dsn in DATABASES.items():
    temp_dir, dump_file_path = create_database_dump(dsn)
    if dump_file_path:
        object_key = f"dashboard/{database_name}--{timestamp}.sql.gz"
        upload_success = upload_file(dump_file_path, BUCKET_NAME, object_key, s3_client)
        if upload_success:
            list_bucket_contents(BUCKET_NAME, s3_client)
        else:
            print("Upload failed. Cleaning up temporary directory...")
        cleanup_temp_directory(temp_dir)
    else:
        print("Failed to create database dump")

delete_old_backups(BUCKET_NAME, s3_client, days_to_keep=0)
