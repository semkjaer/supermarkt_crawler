import scrapy
from supermarktcrawler.settings import IS_DEV
from supermarktcrawler.items import LinkItem
from datetime import datetime

class JumboSpider(scrapy.Spider):
    name = 'jb_links'
    allowed_domains = ['jumbo.com']
    start_urls = ['https://www.jumbo.com/producten/?offSet=0&pageSize=24']
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.LinkPipeline': 300,
        }
    }
    offset = 0

    def parse(self, response):
        for product in response.xpath('//article[div[a[@class="link"]]]'):
            item = LinkItem()
            #item['aanbieding'] = [x.strip() for x in product.xpath('string(./div[@class="jum-tag-list unstyled"])').getall()] or []
            item['url'] = 'https://www.jumbo.com/'+product.xpath('.//a/@href').get()
            item['tijd'] = datetime.now()
            item['winkel'] = 'jb'

            yield item
        
        # go to next page unless this is last page
        final_page_active = response.xpath('//ul[contains(@class, "pagination")]/li[last()][contains(@class, "current")]')
        if not IS_DEV and not final_page_active or self.offset > 50000:
            self.offset += 24
            yield scrapy.Request(f'https://www.jumbo.com/producten/?offSet={self.offset}&pageSize=24', callback=self.parse)