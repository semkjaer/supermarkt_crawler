import scrapy
import re
import sys
from time import sleep
from supermarktcrawler.settings import IS_DEV, PROXY
from supermarktcrawler.items import SupermarktcrawlerItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class DekamarktSpider(scrapy.Spider):
    name = 'dekamarkt'
    allowed_domains = ['dekamarkt.nl']
    start_urls = ['https://www.dekamarkt.nl']

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

        chromedriver.get('https://www.dekamarkt.nl/boodschappen')
        sleep(10)
        try: 
            chromedriver.find_element(By.XPATH, '//button[contains(text(), "Accepteren")]').click()
        except: 
            pass
        categories = set(x.get_attribute('href') for x in chromedriver.find_elements(By.XPATH, "//a[contains(@href, '/boodschappen/')]"))
        print(chromedriver.find_elements(By.XPATH, "//a[contains(@href, '/boodschappen/')]"))
        products = set()
        # zoekt product urls met selenium: category -> subcategory => extract product links
        for url in categories:
            chromedriver.get(url)
            href = url.split('.nl/')[-1]
            subcategories = set(x.get_attribute('href') for x in chromedriver.find_elements(By.XPATH, f'//ul/li/a[contains(@href, "{href}")]'))

            for link in subcategories:
                chromedriver.get(link)
                href = '/'.join(link.split('/')[4:])
                sleep(1)
                product_links = set(x.get_attribute('href') for x in chromedriver.find_elements(By.XPATH, f'//a[contains(@href, "{href}/")]'))
                products.update(product_links)
                if IS_DEV: break
            if IS_DEV: break
        chromedriver.close()

        for i, url in enumerate(products):
            yield scrapy.Request(url, callback=self.parse_product_page)
            if i == 9 and IS_DEV: break

    def parse_product_page(self, response):
        item = SupermarktcrawlerItem(url=response.url)
        item['naam'] = response.xpath('//h1[@class="product-details__info__title"]/text()').get()
        item['inhoud'] = response.xpath('//span[@class="product-details__info__subtitle"]/text()').get()
        euros = response.xpath('//span[@class="product-card__price__euros"]/text()').get()
        cents = response.xpath('//span[@class="product-card__price__cents"]/text()').get()
        item['prijs'] = euros + cents
        item['omschrijving'] = response.xpath('//div[@class="product-details__extra__content"]/text()').get()
        item['aanbieding'] = response.xpath('//div[@class="product-card__discount"]//text()').getall() or []
        item['categorie'] = [x.strip() for x in response.xpath('//div[@class="bread-crumb"]//a/text()').getall()[:-1]]
        
        yield item
