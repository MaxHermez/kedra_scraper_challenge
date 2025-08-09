from dagster import ConfigurableResource, EnvVar
from pymongo import MongoClient
import boto3


class SettingsResource(ConfigurableResource):
    clean_bucket: str = EnvVar("CLEAN_BUCKET")


class MongoResource(ConfigurableResource):
    uri: str = EnvVar("MONGO_URI")
    db: str = EnvVar("MONGO_DB")
    landing_col: str = EnvVar("MONGO_LANDING_COL")
    processed_col: str = EnvVar("MONGO_PROCESSED_COL")

    @property
    def client(self):
        return MongoClient(self.uri)[self.db]
    
    @property
    def landing(self):
        return self.client[self.landing_col]

    @property
    def processed(self):
        return self.client[self.processed_col]


class MinioResource(ConfigurableResource):
    endpoint: str = EnvVar("MINIO_ENDPOINT")
    access_key: str = EnvVar("MINIO_ACCESS_KEY")
    secret_key: str = EnvVar("MINIO_SECRET_KEY")
    landing_bucket: str = EnvVar("LANDING_BUCKET")
    clean_bucket: str = EnvVar("CLEAN_BUCKET")

    @property
    def client(self):
        return boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
