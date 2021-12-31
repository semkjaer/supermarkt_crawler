import scrapy
import re
import sys
import pymongo
from time import sleep
from datetime import datetime
from supermarktcrawler.settings import IS_DEV, PROXY, MONGO_DATABASE, MONGO_URI
from supermarktcrawler.items import LinkItem, ProductItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class DekamarktSpider(scrapy.Spider):
    name = 'dk_products'
    allowed_domains = ['dekamarkt.nl']
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    col = db['links']
    doc = col.find({'winkel' : 'dk'})
    start_urls = [x['url'] for x in list(doc)]
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.ProductPipeline': 300,
        }
    }

    def parse(self, response):
        item = ProductItem(url=response.url)
        item['naam'] = response.xpath('//h1[@class="product-details__info__title"]/text()').get()
        item['inhoud'] = response.xpath('//span[@class="product-details__info__subtitle"]/text()').get()
        euros = response.xpath('//span[@class="product-card__price__euros"]/text()').get()
        cents = response.xpath('//span[@class="product-card__price__cents"]/text()').get()
        item['prijs'] = euros + cents
        item['omschrijving'] = response.xpath('//div[@class="product-details__extra__content"]/text()').get()
        #item['aanbieding'] = response.xpath('//div[@class="product-card__discount"]//text()').getall() or []
        item['categorie'] = [x.strip() for x in response.xpath('//div[@class="bread-crumb"]//a/text()').getall()[:-1]]
        item['tijd'] = datetime.now()
        
        yield item
