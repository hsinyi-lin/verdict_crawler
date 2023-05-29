# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VerdictItem(scrapy.Item):
    title = scrapy.Field()
    judgement_date = scrapy.Field()
    year = scrapy.Field()
    crime_id = scrapy.Field()
    crime_name = scrapy.Field()
    url = scrapy.Field()
    ver_title = scrapy.Field()
    sub_title = scrapy.Field()
    result = scrapy.Field()
    incident = scrapy.Field()
    incident_lite = scrapy.Field()
    laws = scrapy.Field()
