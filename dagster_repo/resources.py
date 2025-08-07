from dagster import ConfigurableResource
from pymongo import MongoClient
from minio import Minio

class MongoResource(ConfigurableResource):
    uri: str
    db: str

    def client(self) -> MongoClient:
        return MongoClient(self.uri)[self.db]

class MinioResource(ConfigurableResource):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool = False

    def client(self) -> Minio:
        return Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )
