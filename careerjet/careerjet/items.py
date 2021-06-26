# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CareerjetItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Title = scrapy.Field()
    Location = scrapy.Field()
    Salary = scrapy.Field()
    EmploymentType = scrapy.Field()
    EmployerName = scrapy.Field()
    JobDescription = scrapy.Field()
    ApplyLink = scrapy.Field()
    PostedAt = scrapy.Field()
    JobURL = scrapy.Field()
    Source = scrapy.Field()
