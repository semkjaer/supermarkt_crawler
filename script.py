#!/usr/bin/python

import os
from supermarktcrawler.spiders import dekamarkt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# spiders = os.popen('scrapy list').read()
process = CrawlerProcess(get_project_settings())
process.crawl('dekamarkt')
process.crawl('albert_heijn')
#process.crawl('jumbo')
process.crawl('vomar')
process.start()