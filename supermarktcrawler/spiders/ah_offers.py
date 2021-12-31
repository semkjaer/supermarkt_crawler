from time import sleep
from datetime import datetime
from supermarktcrawler.items import OfferItem
import scrapy
from supermarktcrawler.settings import IS_DEV, PROXY
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
import re


class AlbertHeijnSpider(scrapy.Spider):
    name = 'ah_offers'
    allowed_domains = ['ah.nl']
    start_urls = ['https://www.ah.nl/bonus']
    custom_settings = {
        'ITEM_PIPELINES' : {
            'supermarktcrawler.pipelines.OfferPipeline': 300,
        }
    }

    def parse(self, response):
        platforms = {
            'linux' : '/usr/lib/chromium-browser/chromedriver',
            'win32' : r'C:\Users\SemKj\Downloads\chromedriver_win32\chromedriver'
        }
        options = Options()
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL",

        }

        webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True
        options.headless = True
        chromedriver = webdriver.Chrome(executable_path=platforms[sys.platform], options=options)

        chromedriver.get('https://www.ah.nl/bonus')
        sleep(5)
        categories = chromedriver.find_elements(By.XPATH, '//h3[contains(@class, "typography_root") and not(contains(text(), "Gall")) and not(contains(text(), "Online")) and not(contains(text(), "Etos"))]/following-sibling::div/div/a')
        for category in set(categories):
            chromedriver.get(category.get_attribute('href'))
            sleep(4)
            products = chromedriver.find_elements(By.XPATH, '//article')
            for product in set(products):
                item = OfferItem()
                link = product.find_element(By.XPATH, '//a[contains(@href, "/product/")]')
                item['url'] = '/'.join([x for x in link.get_attribute('href').split('/') if x != 'volgende-week'])
                item['aanbieding'] = product.find_element(By.XPATH, '//span[contains(@class, "shield_text")]').text
                item['winkel'] = 'ah'
                item['tijd'] = datetime.now()

                yield item