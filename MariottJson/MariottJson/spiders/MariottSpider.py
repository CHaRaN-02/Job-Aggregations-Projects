import scrapy
import datetime
import time
import json
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest, request
from scrapy.selector import Selector
from scrapy.http.request import Request
from MariottJson import items
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class genSpider(scrapy.Spider):
    name = 'Mariott'
    allowed_domains = 'jobs.marriott.com'
    page = 1
    limit = 2
    # base_url = 'https://careers.mcdonalds.com/main/jobs?keywords=&page={}'.format(page)
    start_urls = [
        "https://jobs.marriott.com/api/jobs?page=1&sortBy=relevance&descending=false&internal=false"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.handle_error
            )

    def parse(self, response):
        # sel = Selector(response)
        # print(response.body)
        data = json.loads(response.body)
        # jobs = data.get("data").get("jobs")
        print("num of jobs = ",len(data['jobs']))
        # count = 0
        for job in data['jobs']:
            location_list = ["city", "state", "country", "country_code", "postal_code"]
            str_count = 0
            location_string = ''
            item = items.MariottjsonItem()
            for key, value in job['data'].items():
                if key == 'slug':
                    item['JobID'] = value
                    url = "https://jobs.marriott.com/marriott/jobs/"
                    url += value
                    # print("url = ",url)
                    item['JobLink'] = url
                elif key == 'title':
                    item['Title'] = value
                elif key == 'description':
                    cleantext = BeautifulSoup(value, "lxml").text
                    item['Description'] = cleantext.replace('\t', "").replace("\xa0", "").replace("\n", "").replace(
                        "\r", "").strip()
                    # print(value)
                elif key == 'create_date':
                    item['PostedAt'] = value
                elif key in location_list:
                    location_string += value + ' '
                    str_count += 1
                    if len(location_list) == str_count:
                        item['Location'] = location_string
                        location_string = ''
                elif key == 'apply_url':
                    item['ApplyLink'] = value
                elif key == 'meta_data':
                    val = job['data'][key]['googlejobs']['derivedInfo']['jobCategories']
                    str_val = str(val)
                    item['JobFunction'] = str_val.replace("[","").replace("]","")
                elif key == 'experience_levels':
                    item['Experience'] = value
                elif key == 'employment_type':
                    item['EmploymentType'] = value
                elif key == 'industry':
                    item['EmploymentIndustry'] = value
            yield item

        if len(data['jobs']) != 0:
            self.page += 1
            print(self.page)
            url = "https://jobs.marriott.com/api/jobs?page={}&sortBy=relevance&descending=false&internal=false".format(self.page)
            yield scrapy.Request(
                url=url,
                dont_filter= True,
                callback=self.parse,
                errback=self.handle_error
            )

        # job_postings = sel.css(".search-result-item.ng-star-inserted").extract()
        # print("len = ", len(job_postings))

    def handle_error(self, failure):

        self.logger.error(repr(failure))

        if failure.check(HttpError):

            # these exceptions come from HttpError spider middleware

            # you can get the non-200 response

            response = failure.value.response

            print('HttpError on', response.url, response)

            self.logger.error('HttpError on %s', response.url)

            raise Exception('HttpError on {}'.format(response.body))

        elif failure.check(DNSLookupError):

            # this is the original request

            request = failure.request

            print('DNSLookupError on ', request.url)

            self.logger.error('DNSLookupError on %s', request.url)

            raise Exception('DNSLookupError on {}'.format(request.body))

        elif failure.check(TimeoutError, TCPTimedOutError):

            request = failure.request

            print('TimeoutError on ', request.url)

            self.logger.error('TimeoutError on %s', request.url)

            raise Exception('TimeoutError on {}'.format(request.body))

        else:

            request = failure.request

            print('UnKnown Error on ', request.url)

            self.logger.error('UnKnown Error on %s', request.url)

            raise Exception('UnKnown Error on : {}'.format(request.body))
