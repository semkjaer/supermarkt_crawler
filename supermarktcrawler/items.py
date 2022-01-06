# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    sku = scrapy.Field()
    naam = scrapy.Field()
    omschrijving = scrapy.Field()
    inhoud = scrapy.Field()
    kenmerken = scrapy.Field()
    prijs = scrapy.Field()
    categorie = scrapy.Field()
    tijd = scrapy.Field()
    winkel = scrapy.Field()

class OfferItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    aanbieding = scrapy.Field()
    tijd = scrapy.Field()
    winkel = scrapy.Field()

class LinkItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    tijd = scrapy.Field()
    winkel = scrapy.Field()