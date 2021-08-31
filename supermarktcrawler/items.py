# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SupermarktcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    naam = scrapy.Field()
    omschrijving = scrapy.Field()
    inhoud = scrapy.Field()
    kenmerken = scrapy.Field()
    prijs = scrapy.Field()
    aanbieding = scrapy.Field()
    categorie = scrapy.Field()