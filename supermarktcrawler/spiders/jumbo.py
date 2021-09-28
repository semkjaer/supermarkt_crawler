import scrapy
from supermarktcrawler.settings import IS_DEV
from supermarktcrawler.items import SupermarktcrawlerItem

class JumboSpider(scrapy.Spider):
    name = 'jumbo'
    allowed_domains = ['jumbo.com']
    start_urls = ['https://www.jumbo.com/producten/?offSet=0&pageSize=24']
    offset = 0

    def parse(self, response):
        print(response.request.meta)
        print(response.meta)
        for product in response.xpath('//div[div[a[contains(@class, "jum-product-card")]]]'):
            item = SupermarktcrawlerItem()
            item['aanbieding'] = [x.strip() for x in product.xpath('.//ul[contains(@class, "jum-tag-list unstyled")]//span/text()').getall()] or []
            url = 'https://www.jumbo.com/'+product.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, meta={'item': item})

        # go to next page unless this is last page
        final_page_active = response.xpath('//ul[contains(@class, "pagination")]/li[last()][contains(@class, "current")]')
        if not IS_DEV and not final_page_active or self.offset > 50000:
            self.offset += 24
            yield scrapy.Request(f'https://www.jumbo.com/producten/?offSet={self.offset}&pageSize=24', callback=self.parse)

    def parse_product(self, response, meta=None):
        item = response.meta['item']
        item['url'] = response.url
        item['naam'] = response.xpath('//h1/text()').get()
        price = response.xpath('//div[@class="current-price"]')
        euros = price.xpath('./span/text()').get()
        cents = price.xpath('./sup/text()').get()
        item['prijs'] = f'{euros}.{cents}'
        item['inhoud'] = response.xpath('//h2/text()').get()
        item['categorie'] = [x.strip() for x in response.xpath('//ol[@class="breadcrumb-trail"]//a/text()').getall()]
        
        yield item
        # fetch additional data
        # sku = response.url.split('-')[-1]
        # yield scrapy.Request('https://www.jumbo.com/api/frontstore-api', method='POST', body='''{"query":"\n  fragment productFields on Product {\n    id: sku\n    brand\n    ean\n    category\n    categories {\n      name\n      path\n      id\n    }\n    subtitle\n    title\n    image\n    inAssortment\n    canonicalUrl\n    description\n    storage\n    recycling\n    ingredients\n    isRetailSet: retailSet\n    isMedicine\n    preparation: preparationAndUsage\n    thumbnails {\n      image\n      type\n    }\n    additionalImages {\n      image\n      type\n    }\n    allergies {\n      id\n      name\n    }\n    nutritionsTable{\n      columns\n      rows\n    }\n    availability {\n      label\n      isAvailable\n      availability\n    }\n    link\n    prices: price {\n      price\n      promoPrice\n      pricePerUnit {\n        price\n        unit\n      }\n    }\n    quantityOptions {\n      maxAmount\n      minAmount\n      stepAmount\n      unit\n    }\n    primaryBadge: primaryBadges {\n      alt\n      image\n    }\n    secondaryBadges {\n      alt\n      image\n    }\n    promotions {\n      id\n      attachments{\n        type\n        path\n      }\n      tags {\n        text\n        inverse\n      }\n      group\n      isKiesAndMix\n      image\n      url\n      duration {\n        pdpFormatted\n        pdpGetUntil\n      }\n    }\n    manufacturer {\n      description\n      address\n      phone\n      website\n    }\n  }\n\n\n  query product($sku: String!) {\n    product(sku: $sku) {\n      ...productFields\n      retailSetProducts {\n        ...productFields\n      }\n      alternatives {\n        ...productFields\n      }\n      crossSells {\n        ...productFields\n      }\n    }\n  }\n","variables":
        #                             {"sku":"''' + sku + '"},"operationName":"product"}', callback=self.parse_json, meta={'item': item})

