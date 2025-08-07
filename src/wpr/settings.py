# Scrapy settings for kedra_scraper_challenge project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_NAME = "kedra_scraper_challenge"

SPIDER_MODULES = ["src.wpr.spiders"]
NEWSPIDER_MODULE = "src.wpr.spiders"

ADDONS = {}

# Autothrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_TARGET_CONCURRENCY = 10.0

TELNETCONSOLE_USERNAME = "scrapy"
TELNETCONSOLE_PASSWORD = "scrapy"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "kedra_scraper_challenge (+http://www.yourdomain.com)"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    'src.wpr.pipelines.file_storage.FileStoragePipeline': 300,
    'src.wpr.pipelines.mongo.MongoPipeline':               400,
}
# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# Environment-based configuration
# MinIO/S3 settings
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY') 
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'wpr-landing')
MINIO_PREFIX = os.getenv('MINIO_PREFIX', 'raw/')

# MongoDB settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:rootpassword@mongodb:27017')
MONGO_DB = os.getenv('MONGO_DB', 'wpr_landing')
MONGO_COL = os.getenv('MONGO_COL', 'decisions')

