import scrapy
import re
import pymongo
from datetime import datetime
from supermarktcrawler.settings import IS_DEV, MONGO_URI, MONGO_DATABASE
from supermarktcrawler.items import ProductItem

class JumboSpider(scrapy.Spider):
    name = 'vm_products'
    allowed_domains = ['vomar.nl']
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    col = db['links']
    doc = col.find({'winkel' : 'vm'})
    start_urls = [x['url'] for x in list(doc)]
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.ProductPipeline': 300,
        }
    }

    def parse(self, response):
        item = ProductItem(url=response.url)
        item['naam'] = response.xpath('//h1/text()').get()
        item['prijs'] = re.sub(' ', '', ''.join(response.xpath('//p[@class="price"]//child::text()').getall()))
        item['inhoud'] = response.xpath('//p[@class="price"]/preceding-sibling::p[last()]/text()').get()
        item['omschrijving'] = response.xpath('//p[@class="price"]/parent::*/p/text()').get()
        item['categorie'] = [x for x in response.xpath('//div[@class="breadcrumb-container"]//a/text()').getall() if not x == 'Assortiment']
        item['tijd'] = datetime.now()

        yield item