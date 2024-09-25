import os
import shutil
import subprocess
import tempfile

from datetime import datetime
from pathlib import Path

import boto3
import sentry_sdk

from minicli import cli, run

if sentry_dsn := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=sentry_dsn)

# thoses databases will be backuped and uploaded to S3
DATABASES: dict[str, str] = {
    "dashboard": os.getenv("DATABASE_URL", ""),
    "dashboard_backend": os.getenv("DOKKU_POSTGRES_AQUA_URL", ""),
}
BUCKET_NAME: str = "ecospheres-backups"


def connect_to_s3():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="nl-ams",
        endpoint_url="https://s3.nl-ams.scw.cloud",
    )


@cli
def list_bucket_contents(bucket_name: str = BUCKET_NAME):
    s3_client = connect_to_s3()
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    print(f"Contents of {bucket_name}:")
    for obj in response.get("Contents", []):
        print(obj["Key"])


@cli
def upload_dummy_file():
    file_path = Path("/Users/alexandre/Captures d'écran/Capture d’écran 2024-09-25 à 16.36.03.png")
    upload_file(file_path, BUCKET_NAME, "dashboard/aaa--bbb.sql.gz")


def upload_file(local_file_path: Path, bucket_name: str, object_key: str) -> bool:
    s3_client = connect_to_s3()
    s3_client.upload_file(local_file_path, bucket_name, object_key)
    print("File uploaded successfully")
    return True


def create_database_dump(dsn: str, dummy_dump: bool = False) -> tuple[str | None, Path | None]:
    # Create a temporary directory for the dump file
    temp_dir = tempfile.mkdtemp()
    dump_file_path = Path(temp_dir) / "database_dump.sql.gz"

    if dummy_dump:
        # create a dummy dump file in temp_dir
        with open(dump_file_path, "w") as f:
            f.write("dummy dump")
    else:
        command = f"pg_dump '{dsn}' | gzip > {dump_file_path}"
        subprocess.run(command, shell=True, check=True)

    return temp_dir, dump_file_path


def cleanup_temp_directory(temp_dir: str):
    shutil.rmtree(temp_dir)
    print("Temporary directory cleaned up successfully")


@cli
def delete_old_files(bucket_name: str = BUCKET_NAME, days_to_keep: int = 7):
    s3_client = connect_to_s3()
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
        print(f"Deleted {len(objects_to_delete)} old files")
    else:
        print("No old files found to delete")


@cli
def backup(bucket_name: str = BUCKET_NAME, dummy_dump: bool = False):
    """Backup databases to S3"""
    print("Starting backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for database_name, dsn in DATABASES.items():
        object_key = f"dashboard/{database_name}--{timestamp}.sql.gz"
        temp_dir, dump_file_path = create_database_dump(dsn, dummy_dump=dummy_dump)
        if dump_file_path and temp_dir:
            upload_success = upload_file(dump_file_path, bucket_name, object_key)
            if upload_success:
                list_bucket_contents(bucket_name)
            else:
                print("Upload failed. Cleaning up temporary directory...")
            cleanup_temp_directory(temp_dir)
        else:
            print("Failed to create database dump")
    delete_old_files(bucket_name)


if __name__ == "__main__":
    run()
