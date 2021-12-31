#//a[contains(text(), "Bekijk")]

import scrapy
from supermarktcrawler.settings import IS_DEV, MONGO_URI, MONGO_DATABASE
from supermarktcrawler.items import OfferItem, ProductItem
from datetime import date, datetime
import pymongo

class JumboSpider(scrapy.Spider):
    name = 'jb_offers'
    allowed_domains = ['jumbo.com']
    start_urls = ['https://www.jumbo.com/aanbiedingen/alles']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES' : {
            'rotating_proxies.middlewares.RotatingProxyMiddleware': None,
            'rotating_proxies.middlewares.BanDetectionMiddleware': None
        },
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.OfferPipeline': 300,
        }
    }

    def parse(self, response):
        aanbiedingen = response.xpath('//a[contains(text(), "Bekijk")]/@href').getall()
        for href in aanbiedingen:
            if len(href.split('/')) == 4:
                yield scrapy.Request('https://www.jumbo.com'+href, callback=self.parse_aanbieding)

    def parse_aanbieding(self, response):
        products = response.xpath('//article')
        #//article//div[@class="promotions"]/span/text()
        for product in products:
            item = OfferItem()
            item['url'] = 'https://www.jumbo.com' + product.xpath('.//a/@href').get()
            item['aanbieding'] = ' '.join([x.strip() for x in product.xpath('.//div[@class="promotions"]/descendant::*/text()').getall()])
            item['winkel'] = 'jb'
            item['tijd'] = datetime.now()

            if item['aanbieding'] != 'Niet beschikbaar':
                yield item