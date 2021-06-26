# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MariottjsonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Title = scrapy.Field()
    JobLink = scrapy.Field()
    JobFunction = scrapy.Field()
    JobID = scrapy.Field()
    Location = scrapy.Field()
    EmploymentType = scrapy.Field()
    Description = scrapy.Field()
    PAGE = scrapy.Field()
    PostedAt = scrapy.Field()
    EmployerName = scrapy.Field()
    ApplyLink = scrapy.Field()
    Source = scrapy.Field()
    Experience = scrapy.Field()
    EmploymentIndustry = scrapy.Field()
