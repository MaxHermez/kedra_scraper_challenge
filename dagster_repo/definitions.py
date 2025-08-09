from dagster import Definitions
from dagster_repo.resources import MongoResource, MinioResource, SettingsResource
from dagster_repo.assets import landing_scrape, transform_docs
from dagster_repo.schedules import schedule, job

defs = Definitions(
    assets=[landing_scrape, transform_docs],
    jobs=[job],
    schedules=[schedule],
    resources={
        "mongo": MongoResource(),
        "minio": MinioResource(),
        "settings": SettingsResource(),   # <- add this
    },
)
