#!/usr/bin/python

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# spiders = os.popen('scrapy list').read()
process = CrawlerProcess(get_project_settings())
process.crawl('dk_products')
process.crawl('ah_products')
process.crawl('jb_products')
process.crawl('vm_products')
process.start()