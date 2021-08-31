# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from supermarktcrawler.settings import IS_DEV
from .items import SupermarktcrawlerItem
import logging
import pymongo

class SupermarktcrawlerPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if not IS_DEV:
            self.db['products'].replace_one({'url': item['url']}, item, upsert=True)
        return item

# class SupermarktcrawlerPipeline:
#     def __init__(self):
#         self.conn = sqlite3.connect('supermarket.db')
#         self.cursor = self.conn.cursor()
#         self.cursor.execute('''CEATE TABLE IF NOT EXISTS producten (
#             naam TEXT PRIMARY KEY,
#             inhoud TEXT,
#             omschrijving TEXT,
#             kenmerken TEXT,
#             prijs REAL,
#             aanbieding INTEGER
#         )''')

#     def process_item(self, item, spider):
#         item.setdefault('omschrijving', '')
#         item.setdefault('kenmerken', '')
#         self.cursor.execute(f'''INSERT INTO producten VALUES 
#                                 ({item['naam']},{item['inhoud']},{item['omschrijving']},{item['kenmerken']},{float(item['prijs'])},{item['aanbieding']})
#                                 ON CONFLICT(naam) DO UPDATE SET prijs = {float(item['prijs'])};''')
#         return item
