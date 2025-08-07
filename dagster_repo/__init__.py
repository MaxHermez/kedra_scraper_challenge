from dagster import Definitions
from .assets.scrape_asset import scrape_asset
from .assets.transform_asset import transform_asset
from .jobs import scrape_job
from .schedules import daily_scrape

defs = Definitions(
    assets=[scrape_asset, transform_asset],
    jobs=[scrape_job],
    schedules=[daily_scrape],
)