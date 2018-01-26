import scrapy
from scrapinho.items import TestItem


class QuotesSpider(scrapy.Spider):
    name = "testes"

    def start_requests(self):
        urls = [
            'https://docs.scrapy.org/en/latest/topics/exporters.html#topics-exporters'
        ] * 10
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        it = response.css('div.section h1::text').extract()
        return TestItem(some_attribute=it)

