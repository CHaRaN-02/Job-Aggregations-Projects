#Author : Sai Charan
import scrapy
import json
import time
from bs4 import BeautifulSoup
import re
import datetime
from careerjet import items
from scrapy_splash import SplashRequest
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class CareerSpider(scrapy.Spider):
    name = 'career'
    page = 1
    page_limit = 100
    allowed_domains = ['careerjet.co.in']
    def __init__(self):
        state = {}
        try:
            file = open('state.json', 'r')
            state = json.loads(file.read())
        except Exception as e:
            pass
        self.page_no = state.get("page_no", 1)
        self.url = 'https://www.careerjet.co.in/jobs-in-india-83624.html?p=1'
        base_url = state.get('url', self.url)
        self.jobs_fetched = state.get("jobs_fetched", 0)
        self.start_urls = [base_url]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                args={'wait': 10},
                meta={'retry_times': 5},
            )

    def parse(self, response):
        #################### Extracting Each Field ###########################
        sel = Selector(response)
        ##################### JobCards ############################
        jobs = sel.css('#search-content > ul.jobs > li *').xpath('@href').extract()
        #################### Job URL ############################
        job_urls = []
        for job in jobs:
            job_urls.append('https://www.careerjet.co.in/' + str(job))
        for i in range(len(job_urls)):
            yield SplashRequest(
                            url=job_urls[i],
                            callback=self.parse_results,
                            errback=self.handle_error,
                            priority= self.page_limit+len(job_urls) - i,
                            args={
                                'wait': 20,
                            },
                            meta={
                                'retry_times': 15
                            },
            )
            # break
        if self.page < self.page_limit:
            priority_num = self.page_limit - self.page
            self.page += 1
            self.counter = 0
            next_link = sel.css('#search-content > p > a').xpath('@href').extract()
            next_page = 'https://www.careerjet.co.in/' + str(next_link[-1])
            yield SplashRequest(
                url=next_page,
                callback=self.parse,
                errback=self.handle_error,
                priority=priority_num,
                args={
                    'wait': 20,
                    'timeout': 90,
                    'resource_timeout': 10,
                },
                meta={
                    'retry_times': 5,
                }
            )
    def parse_results(self, response):
        self.counter += 1
        sele = Selector(response)
        item = items.CareerjetItem()

        #################### Job Title ############################
        title = sele.css('#job > div > header > h1::text').extract()
        item['Title'] = title[0]
        company = sele.css('#job > div > header > p::text').extract()
        item['EmployerName'] = company[0].strip()
        link = response.url
        item['JobURL'] = link
        ##################### Details ############################
        block = sele.css('#job > div > header > ul.details > li').extract()
        block_data = []
        for each in block:
            text = each.split('svg>')[1].split('</li')[0].strip()
            if '<span>' in text:
                text = text.split('span>')[1].split('</')[0].strip()
            block_data.append(text)
        if len(block_data) == 3:
            item['Location'] = block_data[0]
            item['EmploymentType'] = block_data[2]
        else:
            item['Location'] = block_data[0]
            item['Salary'] = block_data[1]
            item['EmploymentType'] = block_data[3]
        ##################### Apply Link ############################
        apply = sele.css('#job > div > section.nav > ul > li.col.col-xs-8.col-m-6 > a').xpath('@href').extract()
        apply_link = 'https://www.careerjet.co.in/' + apply[0]
        item['ApplyLink'] = apply_link
        ##################### Posted Date ############################
        posted = sele.css('#job > div > header > ul.tags > li:nth-child(1) > span::text').extract()
        current_time = datetime.datetime.now()
        if 'just' in posted or 'today' in posted or 'minutes' in posted or 'hours' in posted or 'hour' in posted:
            postedAt = current_time
        else:
            if 'month' in posted or 'months' in posted:
                if posted[0].strip().isdigit():
                    no_of_months = int(posted[0].strip())
                else:
                    no_of_months = 1
                months_converted_to_days = 30 * no_of_months
                days_string = str(months_converted_to_days)
            else:
                days = posted[0].replace("+", "").strip()
                if not days.isdigit():
                    days_string = '1'
                else:
                    days_string = days
            postedAt = current_time - datetime.timedelta(days=int(days_string))
        current_time = datetime.datetime.now()
        postedAt = current_time

        time_in_date_time = str(postedAt).split(".")
        time_in_GMT = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.gmtime(time.mktime(time.strptime(time_in_date_time[0],
                                                                          "%Y-%m-%d %H:%M:%S"))))

        item['PostedAt'] = str(time_in_GMT)
        #################### Description############################
        description = sele.css('#job > div > section.content').extract()
        cleantext = BeautifulSoup(description[0], "lxml").text
        item['JobDescription'] = cleantext[1:-1].replace("\n","").strip()
        ##################### Source ############################
        item['Source'] = "https://www.careerjet.co.in/jobs-in-india-83624.html"
        yield item

    def __del__(self):
        state = {
            "url": 'https://www.careerjet.co.in/jobs-in-india-83624.html?p=' + str(self.page_no),
            "page_no": self.page_no,
            "jobs_fetched": self.jobs_fetched,
        }
        # print('................dest................', state)
        state = json.dumps(state, indent=4)
        with open("state.json", "w") as file:
            file.write(state)
        file.close()

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