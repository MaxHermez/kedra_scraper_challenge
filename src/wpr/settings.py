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

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 1

# Configure pipelines
ITEM_PIPELINES = {
    'src.wpr.pipelines.file_storage.FileStoragePipeline': 300,
    'src.wpr.pipelines.mongo.MongoPipeline':               400,
}

# Environment-based configuration
#
# MinIO/S3 settings
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY') 
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'wpr-landing')
MINIO_PREFIX = os.getenv('MINIO_PREFIX', '')

# MongoDB settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:rootpassword@mongodb:27017')
MONGO_DB = os.getenv('MONGO_DB', 'wpr_landing')
MONGO_LANDING_COL = os.getenv('MONGO_LANDING_COL', 'landing_zone')
