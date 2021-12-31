#!/usr/bin/python

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# spiders = os.popen('scrapy list').read()
process = CrawlerProcess(get_project_settings())
process.crawl('dk_offers')
process.crawl('ah_offers')
process.crawl('jb_offers')
# vomar heeft alleen een kortingsfolder in foto format
#process.crawl('vm_offers')
process.start()