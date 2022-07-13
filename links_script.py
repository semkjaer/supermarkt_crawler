#!/usr/bin/python

import os
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

to_crawl = [spider for spider in [x for x in os.popen('scrapy list').read().split('\n') if x] if 'links' in spider]

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    for spider in to_crawl:
        yield runner.crawl(spider)
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished