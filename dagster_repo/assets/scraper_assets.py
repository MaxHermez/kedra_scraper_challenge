import subprocess, json, os
from dagster import asset, AssetExecutionContext
from datetime import datetime
from partitions import monthly

@asset(partitions_def=monthly, required_resource_keys={"mongo"})
def scrape_wpr(context: AssetExecutionContext):
    """
    Kicks off the Scrapy spider inside the *same* container.
    The spider writes metadata + files via Scrapy pipelines.
    """
    start, end = context.partition_key.split("-")
    year, month = map(int, (start, end))
    next_month = month % 12 + 1
    next_year = year + (month // 12)
    start_date = f"{year}-{month:02d}-01"
    end_date   = f"{next_year}-{next_month:02d}-01"

    cmd = [
        "scrapy",
        "crawl",
        "decisions",
        "-a", f"start_date={start_date}",
        "-a", f"end_date={end_date}",
    ]
    context.log.info(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
