import hashlib, os
from w3lib.url import urlparse
from datetime import datetime as dt
from dateutil.parser import parse as dt_parse
from src.wpr.utils.scraping import month_ranges
from src.wpr.items import Decision
import logging

import scrapy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADVANCED_SEARCH_URL = (
    "https://www.workplacerelations.ie/en/search/?advance=true"
)
BASE_SEARCH_URL = (
    "https://www.workplacerelations.ie/en/search/"
    "?decisions=1&from={}&to={}&topic={}&pageNumber={}"
)
URL_DATE_FORMAT = "%d/%m/%Y"
ITEM_DATE_FORMAT = "%Y-%m-%d"



class DecisionsSpider(scrapy.Spider):
    name = "decisions"
    allowed_domains = ["workplacerelations.ie"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.4,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_decision_ids = set()  # Track seen decision IDs

    def __init__(self, start_date="2023-08-05", end_date=None, topics=None, *a, **kw):
        super().__init__(*a, **kw)
        self.seen_decision_ids = set()  # Track seen decision IDs
        self.start_dt_obj = dt_parse(start_date).date()
        self.end_dt_obj = (
            dt_parse(end_date).date() if end_date else dt.today().date()
        )
        self.start_dt = dt_parse(start_date).date().strftime(URL_DATE_FORMAT)
        self.end_dt = (
            dt_parse(end_date).date().strftime(URL_DATE_FORMAT)
            if end_date
            else dt.today().strftime(URL_DATE_FORMAT)
        )
        # -a topics=1,3,42 (set of ints)
        # to avoid having to run all topics each run in dev
        self.topics = {int(t) for t in topics.split(",")} if topics else None

    def start_requests(self):
        yield scrapy.Request(
            ADVANCED_SEARCH_URL,
            callback=self._parse_topics,  # Extract topics from the advanced search page
            dont_filter=True,
        )

    def _parse_topics(self, response: scrapy.http.Response):
        """Extract topics from the advanced search page.

        Args:
            response (scrapy.http.Response): The response object from the request.

        Yields:
            dict: A dictionary containing topic IDs and titles.
        """
        for topic_id, title in self._extract_topics(response).items():
            if self.topics and int(topic_id) not in self.topics:
                continue
            yield from self._crawl_topic(topic_id, title)

    def _crawl_topic(self, topic_id: str, title: str):
        """Crawl through all pages of a specific topic.

        Args:
            topic_id (str): The ID of the topic to crawl.
            title (str): The title of the topic to crawl.

        Yields:
            scrapy.Request: A request for each page of the topic.
        """
        for start, stop in month_ranges(self.start_dt_obj, self.end_dt_obj):
            from_str = start.strftime(URL_DATE_FORMAT)
            to_str   = stop.strftime(URL_DATE_FORMAT)
            part_key = start.strftime("%Y-%m")            # e.g. "2024-01"

            url = BASE_SEARCH_URL.format(from_str, to_str, topic_id, 1)
            yield scrapy.Request(
                url,
                callback=self._parse_listing_page,
                meta={
                    "topic_id": topic_id,
                    "topic_title": title,
                    "partition_date": part_key,
                    "page": 1,
                },
            )

    def _parse_listing_page(self, response: scrapy.http.Response):
        """Parse the listing page for decisions.

        Args:
            response (scrapy.http.Response): The response object from the request.

        Returns:
            None

        Yields:
            scrapy.Request: A request for each decision detail page.
        """
        rows = response.css(".item-list.search-list li")  # every result row
        if not rows:
            return  # end-of-pagination
        next_page = response.meta["page"] + 1
        yield response.follow(
            response.url.replace(f"pageNumber={response.meta['page']}",
                                f"pageNumber={next_page}"),
            callback=self._parse_listing_page,
            meta={**response.meta, "page": next_page},
        )
        for row in rows:
            # extract decision metadata from the search page
            href  = row.css("h2 a::attr(href)").get()
            title = row.css("h2 a::attr(title), h2 a::text").get()
            date  = row.css("span.date::text").get()
            desc  = row.css("p.description::text").get()

            yield response.follow(
                href,
                callback=self._parse_decision,
                meta=response.meta,               # keeps topic & partition
                cb_kwargs={
                    "d_id": title.split()[0] if title else None,
                    "decision_date": date,
                    "description": desc,
                },
            )

    def _parse_decision(self, response: scrapy.http.Response, d_id: str, decision_date: str,  description: str):
        """Parse the decision details from the response.

        Args:
            response (scrapy.http.Response): The response object from the request.
            d_id (str): The decision ID extracted from the listing page.
            date (str): The date of the decision in the search page.
            description (str): The description of the decision in the search page.

        Yields:
            dict: A dictionary containing the decision details.
        """
        # Check for duplicate decision_id
        if d_id and d_id.strip() in self.seen_decision_ids:
            logger.info(f"Skipping duplicate decision_id: {d_id.strip()}")
            return

        # Add to seen set for deduplication
        if d_id:
            self.seen_decision_ids.add(d_id.strip())
        
        item = {
            "partition_date":  response.meta["partition_date"],
            "topic_id":        response.meta["topic_id"],
            "topic_title":     response.meta["topic_title"],
            "decision_id":     d_id.strip(),
            "decision_date":   dt_parse(decision_date.strip(), dayfirst=True).date().strftime(ITEM_DATE_FORMAT),
            "description":     description.strip(),
            "file_source_url": response.url,
        }

        # decide whether this is a binary or an HTML page
        ext = os.path.splitext(urlparse(response.url).path)[-1].lower()
        is_binary = ext in {".pdf", ".doc", ".docx"}

        if is_binary:
            body_bytes = response.body  # raw file bytes
        else:
            body_bytes = response.text.encode()  # save HTML

        item["file_extension"] = ext or (".html" if not is_binary else "")
        item["file_extension"] = item["file_extension"][1:]  # remove leading dot
        item["file_content"]   = body_bytes  # hand to pipeline
        item["file_hash"]      = hashlib.sha256(body_bytes).hexdigest()

        item = Decision(**item)

        yield item

    @staticmethod
    def _extract_topics(response: scrapy.http.Response) -> dict[str, str]:
        """Extract topics from the response.

        Args:
            response (scrapy.http.Response): The response object from the request.

        Returns:
            dict[str, str]: A dictionary mapping topic IDs to their titles.
        """
        values = response.css("#DD4 > option::attr(value)").getall()
        titles = response.css("#DD4 > option::text").getall()
        return {v: t for v, t in zip(values, titles) if v != "-1"}
