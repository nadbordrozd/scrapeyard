# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PolyvoreItem(scrapy.Item):
    title = scrapy.Field()
    breadcrumbs = scrapy.Field()
    orig_price = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    out_url = scrapy.Field()
    url = scrapy.Field()
    image_urls = scrapy.Field()


class PolyvoreSet(scrapy.Item):
    title = scrapy.Field()
    items = scrapy.Field()
    url = scrapy.Field()


class TestItem(scrapy.Item):
    some_attribute = scrapy.Field()
