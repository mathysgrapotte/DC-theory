# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Mtgtop8Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    list_link = scrapy.Field()
    pass
