from time import sleep
from datetime import datetime
from supermarktcrawler.items import ProductItem
import scrapy
from supermarktcrawler.settings import IS_DEV, PROXY, MONGO_URI, MONGO_DATABASE
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
import re
import pymongo
from os import path


class AlbertHeijnSpider(scrapy.Spider):
    name = 'ah_products'
    allowed_domains = ['ah.nl']
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    col = db['links']
    doc = col.find({'winkel' : 'ah'})
    start_urls = [x['url'] for x in list(doc)]
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.ProductPipeline': 300,
        }
    }

    def parse(self, response):
        '''scrape product page'''
        # if path.exists('/media/pi/48A0-4B5F/pages/'):
        #     filename = response.url.split('://')[-1].replace('/', '_')
        #     with open(f'/media/pi/48A0-4B5F/pages/{filename}.html', 'w') as html_file:
        #         html_file.write(response.text)

        item = ProductItem()
        item['url'] = response.url
        item['sku'] = item['url'].split('/')[-2]
        item['naam'] = response.xpath('//h1/span/text()').get()
        item['omschrijving'] = response.xpath('//li[contains(@class, "product-info-description_listItem")]/text()').getall()
        item['inhoud'] = response.xpath('//h4[text()="Inhoud en gewicht"]/following-sibling::p/text()').getall()
        item['kenmerken'] = response.xpath('//h4[text()="Kenmerken"]/following-sibling::ul//text()').getall()
        # prijs staat in 3 spans waar de middelste een punt is eg: '3', '.', '99'
        price = ''.join(response.xpath('//div[contains(@class, "price-amount_root")]/span/text()').getall())
        prijs = re.sub(r'/.', '', price)
        if len(prijs) == 8:
            item['prijs'] = prijs[-4:]
        else:
            item['prijs'] = prijs
        item['categorie'] = [x for x in response.xpath('//ol[contains(@class, "page-navigation_breadcrumbs")]//span/text()').getall() if x not in ['Home', 'Producten']]
        item['tijd'] = datetime.now()

        yield item

