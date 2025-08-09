import hashlib
import boto3
from time import time
from scrapy.exceptions import DropItem


class FileStoragePipeline:
    """
    Saves item['file_content'] to an object-storage bucket and
    sets item['file_path'] to the final key.
    """

    def __init__(self, s3_endpoint, access_key, secret_key,
                 bucket, base_prefix):
        self.s3_endpoint = s3_endpoint
        self.access_key  = access_key
        self.secret_key  = secret_key
        self.bucket      = bucket
        self.base_prefix = base_prefix
        self.s3 = None

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        return cls(
            s.get('MINIO_ENDPOINT'),
            s.get('MINIO_ACCESS_KEY'),
            s.get('MINIO_SECRET_KEY'),
            s.get('MINIO_BUCKET'),
            s.get('MINIO_PREFIX')
        )

    def open_spider(self, spider):
        # Initialize the S3 client
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.s3_endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        # make sure bucket exists
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except:
            self.s3.create_bucket(Bucket=self.bucket)

    def process_item(self, item, spider):
        blob = item.get('file_content')
        if blob is None:
            raise DropItem("Missing file_content")
        hashed = hashlib.sha256(
                f"{item['file_source_url']}{item['partition_date']}{time()}".encode()
            ).hexdigest()
        key = (
            f"{self.base_prefix}"
            f"{item['partition_date']}/"
            f"{hashed}"
        )

        self.s3.put_object(Bucket=self.bucket, Key=key, Body=blob)
        item['file_bucket'] = self.bucket
        item['file_key'] = key

        # Remove raw bytes so Mongo doesn’t store them
        item.pop('file_content', None)
        return item
