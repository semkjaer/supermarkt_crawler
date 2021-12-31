import scrapy
import re
import pymongo
from datetime import datetime
from supermarktcrawler.settings import IS_DEV, MONGO_DATABASE, MONGO_URI
from supermarktcrawler.items import LinkItem

class JumboSpider(scrapy.Spider):
    name = 'vm_links'
    allowed_domains = ['vomar.nl']
    start_urls = ['https://www.vomar.nl/producten']
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.LinkPipeline': 300,
        }
    }

    def parse(self, response):
        categories = response.xpath('//div[@class="col-xs-6 col-md-2 productrange-group"]/a/@href').getall()
        for href in categories:
            yield scrapy.Request('https://www.vomar.nl'+href, callback=self.parse_category)
            if IS_DEV: break

    def parse_category(self, response):
        categories = response.xpath('//div[@class="col-xs-6 col-md-3 department-group"]/a/@href').getall()
        for href in categories:
            yield scrapy.Request('https://www.vomar.nl'+href, callback=self.parse_subcategory)
            if IS_DEV: break

    def parse_subcategory(self, response):
        products = response.xpath('//div[@class="col-md-4 product"]/a/@href').getall()
        for i, href in enumerate(products):
            item = LinkItem()
            item['url'] = 'https://www.vomar.nl' + href
            item['tijd'] = datetime.now()
            item['winkel'] = 'vm'

            yield item