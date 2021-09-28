import scrapy


class CheckIpSpider(scrapy.Spider):
    name = 'check_ip'
    allowed_domains = ['checkip.dyndns.org']
    start_urls = ['http://checkip.dyndns.org/']

    def start_requests(self):
        yield scrapy.Request('http://checkip.dyndns.org/', callback=self.check_ip)
        # yield other requests from start_urls here if needed

    def check_ip(self, response):
        pub_ip = response.xpath('//body/text()').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')[0]
        print("My public IP is: " + pub_ip)
