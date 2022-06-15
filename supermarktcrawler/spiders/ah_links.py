from time import sleep
from datetime import datetime
from supermarktcrawler.items import LinkItem
import scrapy
from supermarktcrawler.settings import IS_DEV, PROXY
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
import re


class AlbertHeijnSpider(scrapy.Spider):
    name = 'ah_links'
    allowed_domains = ['ah.nl']
    start_urls = ['https://www.ah.nl/producten']
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.LinkPipeline': 300,
        }
    }

    # scrapy doet de eerste request automatisch met callback=self.parse
    def parse(self, response):
        '''parse main page -> categories, yield subcategories'''
        platforms = {
            'linux' : '/usr/lib/chromium-browser/chromedriver',
            'win32' : r'C:\Users\SemKj\Downloads\chromedriver_win32\chromedriver'
        }

        options = Options()
        options.headless = True
        webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True

        chromedriver = webdriver.Chrome(executable_path=platforms[sys.platform], options=options)

        categories = {'https://www.ah.nl' + href for href in response.xpath('//a[@data-testhook="taxonomy-main"]/@href').getall()}
        urls = set()
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
        links = response.xpath('//a[contains(@href, "producten/product")]/@href').getall()
        for i, href in enumerate(set(links)):
            item = LinkItem()
            item['url'] = 'https://www.ah.nl' + href
            item['tijd'] = datetime.now()
            item['winkel'] = 'ah'

            yield item