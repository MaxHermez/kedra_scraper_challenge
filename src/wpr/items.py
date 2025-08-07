import scrapy

class Decision(scrapy.Item):
    """
    Represents a decision item scraped from the Workplace Relations website.
    """
    decision_id    = scrapy.Field()
    description    = scrapy.Field()
    decision_date  = scrapy.Field()
    topic_id       = scrapy.Field()
    topic_title    = scrapy.Field()
    partition_date = scrapy.Field()
    file_url       = scrapy.Field()
    file_hash      = scrapy.Field()
    file_extension = scrapy.Field()
    file_content   = scrapy.Field()
    file_path      = scrapy.Field()