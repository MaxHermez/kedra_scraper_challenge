from bs4 import BeautifulSoup
import hashlib
from dagster import asset, AssetExecutionContext
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dagster_repo.partitions import monthly


@asset(partitions_def=monthly)
def landing_scrape(context: AssetExecutionContext):
    start = context.partition_time_window.start
    end   = context.partition_time_window.end
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl('decisions', 
                  start_date=start.isoformat(),
                  end_date=end.isoformat())
    # Start the crawling process, blocking call
    process.start()

@asset(
    required_resource_keys={"mongo","minio","settings"},
    deps=[landing_scrape],
    partitions_def=monthly,
)
def transform_docs(context: AssetExecutionContext):
    start = context.partition_time_window.start
    end   = context.partition_time_window.end

    mongo = context.resources.mongo
    s3    = context.resources.minio
    cfg   = context.resources.settings

    meta = list(mongo.landing.find({"decision_date": {"$gte": start.isoformat(), "$lt": end.isoformat()}}))

    for m in meta:
        ext = m['file_extension']
        file_key = m['file_key']
        identifier = m['decision_id']
        partition = m['partition_date']

        # get metadata from mongo
        landing_doc = s3.client.get_object(Bucket=m['file_bucket'], Key=file_key)['Body'].read()

        # process docs
        if ext in ("html", "htm"):
            soup = BeautifulSoup(landing_doc, "html.parser")
            content = soup.find('div', class_="content")
            out_bytes = content.encode("utf-8")
            out_ext = "html"   # or keep .html after pruning if you prefer
        else:
            out_bytes = landing_doc
            out_ext = ext

        # write to S3
        out_key = f"{partition}/{identifier}.{out_ext}"
        s3.client.put_object(Bucket=cfg.clean_bucket, Key=out_key, Body=out_bytes)

        # prepare new metadata
        new_hash = hashlib.sha256(out_bytes).hexdigest()
        new_meta = dict(m)
        new_meta.update({"file_key": out_key, "file_hash": new_hash})
        source_id = new_meta["_id"]
        new_meta['landing_id'] = source_id
        new_meta.pop("_id", None)

        mongo.processed.update_one({'decision_id': new_meta['decision_id']}, {"$setOnInsert": new_meta}, upsert=True)
