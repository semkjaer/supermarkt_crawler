#!/usr/bin/python

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# spiders = os.popen('scrapy list').read()
process = CrawlerProcess(get_project_settings())
process.crawl('dk_links')
process.crawl('ah_links')
process.crawl('jb_links')
process.crawl('vm_links')
process.start()
