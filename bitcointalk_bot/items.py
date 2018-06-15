# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class BitcointalkPost(scrapy.Item):
    author = scrapy.Field()
    datetime = scrapy.Field()
    topic = scrapy.Field()
    posttext = scrapy.Field()
    identityhash = scrapy.Field()
    signature = scrapy.Field()
