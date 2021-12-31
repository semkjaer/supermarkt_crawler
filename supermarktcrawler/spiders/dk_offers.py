import scrapy
import re
import sys
import pymongo
from time import sleep
from datetime import datetime
from supermarktcrawler.settings import IS_DEV, PROXY, MONGO_DATABASE, MONGO_URI
from supermarktcrawler.items import LinkItem, OfferItem, ProductItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class DekamarktSpider(scrapy.Spider):
    name = 'dk_offers'
    allowed_domains = ['dekamarkt.nl']
    start_urls = ['https://www.dekamarkt.nl/aanbiedingen']
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.OfferPipeline': 300,
        }
    }
    def parse(self, response):
        products = response.xpath('//article')
        for product in products:
            links = product.xpath('./a/@href').getall()
            for href in links:
                if '/boodschappen/' in href:
                    item = OfferItem()
                    item['url'] = 'https://www.dekamarkt.nl' + href
                    item['aanbieding'] = ' '.join(product.xpath('./div[contains(@class, "discount")]/descendant::*/text()').getall())
                    item['tijd'] = datetime.now()
                    item['winkel'] = 'dk'
                    yield item

                elif '/aanbiedingen/' in href:
                    yield scrapy.Request('https://www.dekamarkt.nl'+href, callback=self.parse)