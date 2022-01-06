import scrapy
from supermarktcrawler.settings import IS_DEV, MONGO_URI, MONGO_DATABASE
from supermarktcrawler.items import ProductItem
from datetime import datetime
import pymongo
from os import path

class JumboSpider(scrapy.Spider):
    name = 'jb_products'
    allowed_domains = ['jumbo.com']
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    col = db['links']
    doc = col.find({'winkel' : 'jb'})
    start_urls = [x['url'] for x in list(doc)]
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.ProductPipeline': 300,
        }
    }

    def parse(self, response):
        if path.exists('~/media/pi/48A0-4B5F/pages/'):
            filename = response.url.split('://')[-1].replace('/', '_')
            with open(f'/media/pi/48A0-4B5F/pages/{filename}.html', 'w') as html_file:
                html_file.write(response.text)

        item = ProductItem()
        item['url'] = response.url
        item['sku'] = item['url'].split('-')[-1]
        item['naam'] = response.xpath('//h1/text()').get()
        price = response.xpath('//div[@class="current-price"]')
        euros = price.xpath('./span/text()').get()
        cents = price.xpath('./sup/text()').get()
        item['prijs'] = f'{euros}.{cents}'
        item['inhoud'] = response.xpath('//h2/text()').get()
        item['categorie'] = [x.strip() for x in response.xpath('//ol[@class="breadcrumb-trail"]//a/text()').getall()]
        item['tijd'] = datetime.now()
        
        yield item
        # fetch additional data
        # sku = response.url.split('-')[-1]
        # yield scrapy.Request('https://www.jumbo.com/api/frontstore-api', method='POST', body='''{"query":"\n  fragment productFields on Product {\n    id: sku\n    brand\n    ean\n    category\n    categories {\n      name\n      path\n      id\n    }\n    subtitle\n    title\n    image\n    inAssortment\n    canonicalUrl\n    description\n    storage\n    recycling\n    ingredients\n    isRetailSet: retailSet\n    isMedicine\n    preparation: preparationAndUsage\n    thumbnails {\n      image\n      type\n    }\n    additionalImages {\n      image\n      type\n    }\n    allergies {\n      id\n      name\n    }\n    nutritionsTable{\n      columns\n      rows\n    }\n    availability {\n      label\n      isAvailable\n      availability\n    }\n    link\n    prices: price {\n      price\n      promoPrice\n      pricePerUnit {\n        price\n        unit\n      }\n    }\n    quantityOptions {\n      maxAmount\n      minAmount\n      stepAmount\n      unit\n    }\n    primaryBadge: primaryBadges {\n      alt\n      image\n    }\n    secondaryBadges {\n      alt\n      image\n    }\n    promotions {\n      id\n      attachments{\n        type\n        path\n      }\n      tags {\n        text\n        inverse\n      }\n      group\n      isKiesAndMix\n      image\n      url\n      duration {\n        pdpFormatted\n        pdpGetUntil\n      }\n    }\n    manufacturer {\n      description\n      address\n      phone\n      website\n    }\n  }\n\n\n  query product($sku: String!) {\n    product(sku: $sku) {\n      ...productFields\n      retailSetProducts {\n        ...productFields\n      }\n      alternatives {\n        ...productFields\n      }\n      crossSells {\n        ...productFields\n      }\n    }\n  }\n","variables":
        #                             {"sku":"''' + sku + '"},"operationName":"product"}', callback=self.parse_json, meta={'item': item})