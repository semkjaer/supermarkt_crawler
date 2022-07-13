#!/usr/bin/python

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

to_crawl = [spider for spider in [x for x in os.popen('scrapy list').read().split('\n') if x] if 'offers' in spider]

process = CrawlerProcess(get_project_settings())
for spider in to_crawl:
    process.crawl(spider)
    process.start()