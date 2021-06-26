import json
import scrapy
import datetime
import time

from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest
from scrapy.selector import Selector
from scrapy.http.request import Request
from Quest import items
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class QdSpider(scrapy.Spider):
    name = 'qd'
    allowed_domains = ['careers.questdiagnostics.com']
    start_urls = ['http://careers.questdiagnostics.com/']

    def __init__(self):
        self.priority = 0

        self.jobs_fetched = 0
        self.total_jobs = 10000  # default value
        state = {}
        try:
            file = open('state.json', 'r')
            state = json.loads(file.read())
        except Exception as e:
            pass
        print(state)
        self.page = state.get("page", 1)
        self.url = 'https://careers.questdiagnostics.com/en-US/search?keywords=&location=&pagenumber=1'
        base_url = state.get('url', self.url)
        self.jobs_fetched = state.get("jobs_fetched", 0)
        self.start_urls = [base_url]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                args={
                    'timeout': 90,
                },
                meta={
                    'retry_times': 10,
                }
            )

    # This method makes asynchronous request calls to job postings in current webpage and also moves to next page
    # if jobs fetched is less than total jobs

    def parse(self, response):
        sel = Selector(response)
        total_job = sel.css('.job-result-title').xpath('@href').extract()
        jobs = []
        for each in total_job:
            job = 'https://careers.questdiagnostics.com/' + str(each)
            jobs.append(job)
        self.jobs_fetched += len(jobs)
        for i in range(len(jobs)):
            yield SplashRequest(
                url=jobs[i],
                callback=self.parse_results,
                errback=self.handle_error,
                priority=self.page - i,  # setting priority to order request calls
                args={
                    'wait': 20,
                    'timeout': 90,  # setting timeout as 90 to avoid gateway timeout error
                    'resource_timeout': 10,
                },
                meta={
                    'retry_times': 15
                },

            )
            # break

        # move to next page only if current page is less than the page limit (or)
        # move to next page only if jobs_fetched is less than total jobs found to make dynamic transition between pages

        if self.jobs_fetched < self.total_jobs:
            priority_num = self.page - 5  # assigning priority to order request calls
            self.page += 1
            next_page = 'https://careers.questdiagnostics.com/en-US/search?keywords=&location=&pagenumber={}'.format(self.page)
            yield SplashRequest(
                url=next_page,
                callback=self.parse,
                errback=self.handle_error,
                priority=priority_num,
                args={
                    'timeout': 90,  # setting timeout as 90 to avoid gateway timeout error
                },
                meta={
                    'retry_times': 5,
                }
            )

    # This method also makes asynchronous request calls to all job postings in current webpage

    def parse_results(self, response):
        # self.counter += 1
        item = items.QuestItem()
        sele = Selector(response)
        snapshot = sele.css('#jdp-job-snapshot-section > div > ul > li *::text').extract()
        item['EmploymentType'] = snapshot[5]
        location = sele.css('#jdp-job-snapshot-section > div > ul > li.job-location > div > a > span ::text').extract()
        item['Location'] = location[0]
        employment_industry = sele.css('#jdp-job-snapshot-section > div > ul > li.job-categories > div > div > a ::text').extract()
        item['EmploymentIndustry'] = employment_industry[0]
        item['JobID'] = snapshot[-3]
        posted = snapshot[-11]
        posted_info = posted.split('/')
        date = str(posted_info[2]) + "-" + str(posted_info[1]) + "-" + str(posted_info[0])
        item['PostedAt'] = date
        title = sele.css('#jdp-title-job-title > span.jdp-title-job-title ::text').extract()
        job_title = title[0].split(location[0])
        item['Title'] = job_title[0].replace("-","")
        description = sele.css('#jdp-job-description-section > div ::text').extract()
        descr = []
        for each in description:
            cleaned_description = each.replace("\xa0","").replace('\n','').replace('\r','').strip()
            descr.append(cleaned_description)
        item['JobDescription'] = "".join(descr[2:-1])
        item['Source'] = 'Quest Diagnostics'
        item['JobURL'] = response.url
        yield item
    def __del__(self):
        state = {
            "url": 'https://careers.questdiagnostics.com/en-US/search?keywords=&location=&pagenumber=' + str(self.page),
            "page_no": self.page,
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

