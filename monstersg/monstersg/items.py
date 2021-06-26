# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MonstersgItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    JobTitle = scrapy.Field()
    Location = scrapy.Field()
    Industry = scrapy.Field()
    JobFunction = scrapy.Field()
    JobRole = scrapy.Field()
    Salary = scrapy.Field()
    Currency = scrapy.Field()
    EmploymentType = scrapy.Field()
    Experience = scrapy.Field()
    EmployerName = scrapy.Field()
    EmploymentIndustry = scrapy.Field()
    JobDescription = scrapy.Field()
    JobQualifications = scrapy.Field()
    JobApplyLink = scrapy.Field()
    JobID = scrapy.Field()
    PostedAt = scrapy.Field()
    JobURL = scrapy.Field()
    Skills = scrapy.Field()
    Source = scrapy.Field()
    pass
