from pymongo import MongoClient


class MongoPipeline:
    """
    Inserts the (now lightweight) item into MongoDB.
    """
    def __init__(self, uri, db_name, collection):
        self.uri         = uri
        self.db_name     = db_name
        self.collection  = collection
        self.client      = None
        self.col         = None

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        return cls(
            s.get('MONGO_URI'),
            s.get('MONGO_DB'),
            s.get('MONGO_COL'),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.uri)
        self.col    = self.client[self.db_name][self.collection]
        # Optional: create index on decision_id + partition_date, etc.

    def process_item(self, item, spider):
        # PyMongo can take a Scrapy Item or dict directly
        self.col.update_one(
            {'decision_id': item['decision_id']},
            {'$setOnInsert': dict(item)},
            upsert=True,
        )
        return item

    def close_spider(self, spider):
        if self.client:
            self.client.close()
