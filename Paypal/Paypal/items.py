# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PaypalItem(scrapy.Item):
    # define the fields for your item here like:
    Title = scrapy.Field()
    Location = scrapy.Field()
    EmploymentIndustry = scrapy.Field()
    EmploymentType = scrapy.Field()
    JobURL = scrapy.Field()
    JobID = scrapy.Field()
    PostedAt = scrapy.Field()
    Source = scrapy.Field()
    EmployerName = scrapy.Field()
    Experience = scrapy.Field()
    JobDescription = scrapy.Field()
    # pass
