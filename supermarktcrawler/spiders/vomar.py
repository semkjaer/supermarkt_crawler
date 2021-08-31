import scrapy
import re
from supermarktcrawler.settings import IS_DEV
from supermarktcrawler.items import SupermarktcrawlerItem

class JumboSpider(scrapy.Spider):
    name = 'vomar'
    allowed_domains = ['vomar.nl']
    start_urls = ['https://www.vomar.nl/producten']

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
            yield scrapy.Request('https://www.vomar.nl'+href, callback=self.parse_product)
            #if IS_DEV and i == 9: break

    def parse_product(self, response):
        item = SupermarktcrawlerItem(url=response.url)
        item['naam'] = response.xpath('//h1/text()').get()
        item['prijs'] = re.sub(' ', '', ''.join(response.xpath('//p[@class="price"]//child::text()').getall()))
        item['inhoud'] = response.xpath('//p[@class="price"]/preceding-sibling::p[last()]/text()').get()
        item['omschrijving'] = response.xpath('//p[@class="price"]/parent::*/p/text()').get()
        item['categorie'] = [x for x in response.xpath('//div[@class="breadcrumb-container"]//a/text()').getall() if not x == 'Assortiment']

        yield item

