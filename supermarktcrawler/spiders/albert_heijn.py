from time import sleep
from supermarktcrawler.items import SupermarktcrawlerItem
import scrapy
from supermarktcrawler.settings import IS_DEV
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
import re


class AlbertHeijnSpider(scrapy.Spider):
    name = 'albert_heijn'
    allowed_domains = ['ah.nl']
    start_urls = ['https://www.ah.nl/producten']

    # scrapy doet de eerste request automatisch met callback=self.parse
    def parse(self, response):
        '''parse main page -> categories, yield subcategories'''
        platforms = {
            'linux' : '/usr/lib/chromium-browser/chromedriver',
            'win32' : r'C:\Users\SemKj\Downloads\chromedriver_win32\chromedriver'
        }
        options = Options()
        options.headless = True
        chromedriver = webdriver.Chrome(executable_path=platforms[sys.platform], options=options)

        categories = {'https://www.ah.nl' + href for href in response.xpath('//a[@data-testhook="taxonomy-main"]/@href').getall()}
        # gebruikt selenium om alle subcategorieen te krijgen
        for i, category_url in enumerate(categories):
            chromedriver.get(category_url)
            sleep(1)
            try: # sluit cookie venster indien nodig
                chromedriver.find_element(By.XPATH, '//button[@id="accept-cookies"]').click()
                sleep(1)
            except: pass
            try: # laat meer subcategorieen zien
                chromedriver.find_element(By.XPATH, '//a[contains(@class, "taxonomy-show-more")]').click()
            except: pass
            sleep(1)
            links = chromedriver.find_elements(By.XPATH, '//a[contains(@class, "taxonomy-child_root")]')
        
            urls = set()
            for link in links: # ?page=... bepaald hoeveel producten weergegeven worden
                url = link.get_attribute('href') + '?page=25'
                if url:
                    urls.add(url)
                if IS_DEV and i == 5: break  # IS_DEV kan in settings.py aangepast worden
            if IS_DEV and i == 2: break 
        chromedriver.close()

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_category)
            if IS_DEV: break


    def parse_category(self, response):
        '''crawl subcategories, yield product pages'''
        # set(list()) to filter duplicates 
        products = response.xpath('//a[contains(@href, "producten/product")]')
        for i, product in enumerate(products):
            item = SupermarktcrawlerItem()
            item['aanbieding'] = product.xpath('.//span[contains(@class, "shield_text")]/text()').getall() or []

            yield scrapy.Request('https://www.ah.nl'+product.xpath('@href').get(), 
                                        callback=self.parse_product, meta={'item': item})
            if IS_DEV and i == 9: break


    def parse_product(self, response, meta=None):
        '''scrape product page'''
        item = response.meta['item']
        item['url'] = response.url
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

        yield item

