import scrapy
import time
import re
import datetime

from scrapy_splash import SplashRequest
from scrapy.selector import Selector
from scrapy.http.request import Request
from monstersg import items
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


# import scrapy
#
#
# class MonstersSpider(scrapy.Spider):
#     name = 'monsters'
#     allowed_domains = ['monster.com.sg']
#     start_urls = ['http://monster.com.sg/']
#
#     def parse(self, response):
#         pass
# -*- coding: utf-8 -*-



class MonstersSpider(scrapy.Spider):
    name = 'monsters'

    allowed_domains = ['monster.com.sg']

    start = 0

    limit = 18

    jobs_fetched = 0

    page_limit = 20

    total_jobs = 10000  # default value

    priority = 0

    page = 1

    counter = 0

    base_url = 'https://www.monster.com.sg/srp/results?start={}&sort=1&limit={}&query=data%20science'.format(start, limit)

    # start_urls = ['https://www.monsterindia.com/srp/results?start=' + str(start) + '&sort=1&limit=50&query=,']

    start_urls = [base_url]

    def start_requests(self):

        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                # errback=self.handle_error,
                args={
                    'wait': 10,
                    'timeout': 90,
                    'resource_timeout': 10,
                },
                meta={
                    'retry_times': 5,
                }
            )

    def parse(self, response):

        # print(response, "resp******************", type(response))

        sel = Selector(response)

        # print(sel, "sel**************", type(sel))

        # Get the total count of job postungs available

        total_jobs = sel.css('span.main-heading::text').extract_first()

        if total_jobs:
            total_jobs = total_jobs.strip().split(' ').pop()

        print(total_jobs, 'total_jobs')

        if total_jobs:
            self.total_jobs = int(total_jobs)

        # Get all the job postings that are available in this page

        jobs = sel.xpath("//*[contains(@class, 'job-apply-card')]")

        jobs_urls=[]
        for i in range(len(jobs)):
            sponsored = jobs[i].css("span.sponsr::text").extract_first()
            if sponsored:
                continue
            job_link = jobs[i].css('div.job-tittle a').xpath('@href').extract_first()[2:]
            jobs_urls.append(job_link)
        self.priority = len(jobs_urls)

        # print("jobs",jobs)
        # print()

        jobsLen = len(jobs)

        print('Len', len(jobs))

        # job_url = []
        # for i in range(jobsLen):

        # print(job_url)

        for i in range(len(jobs_urls)):

            yield SplashRequest(
                            url='https:' + '//' + jobs_urls[i],
                            callback=self.parse_results,
                            # errback=self.handle_error,
                            priority= self.page_limit+len(jobs_urls) - i,
                            args={
                                'wait': 20,
                                'timeout': 90,
                                'resource_timeout': 10,
                            },
                            meta={
                                'retry_times': 15
                            },

            )
        if self.page < self.page_limit:
            priority_num = self.page_limit - self.page
            self.page += 1
            self.counter = 0
            self.start += self.limit
            next_page = 'https://www.monster.com.sg/srp/results?start={}&sort=1&limit={}&query=Data%20scientist'.format(self.start, self.limit)
            time.sleep(1)
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

        item = items.MonstersgItem()

        sel = Selector(response)

        item['Location'] = 'Singapore'

        job_title = sel.css("div.job-tittle.detail-job-tittle h1::text").extract_first().replace('\n', '').strip()
        
        item['JobTitle'] = job_title

        employer_name = sel.css("div.job-tittle.detail-job-tittle span *::text").extract_first().replace('\n', '').strip()

        item['EmployerName'] = employer_name

        location = sel.css("span.loc::text").extract_first().replace('\n', '').strip()

        item['Location'] = location

        experience = sel.css("span.exp::text").extract_first()

        if 'fresher' in experience.lower():

            experience_min = 0
            experience_max = 0

        else:

            experience = experience.replace('\n', '').strip().split("-")

            if experience[0].strip().isdigit():

                experience_min = int(experience[0].strip())

            if experience[1].split(" ")[0].isdigit():

                experience_max = int(experience[1].split(" ")[0])

        item['Experience'] = {'min': experience_min, 'max': experience_max}

        salary = sel.css("span.package::text").extract_first().replace('\n', '').strip()

        if salary != 'Not Specified':

            salary = salary.split("-")

            min_value = int(salary[0].replace(",", ""))

            max_value = int(salary[1].replace(",", ""))

            item['Salary'] = {'min': min_value, 'max': max_value}

        else:

            item['Salary'] = salary
        
        employment_type = sel.css("span.color-grey-light::text").extract_first().replace("\n", '').strip()

        item['EmploymentType'] = employment_type

        if 'permanent' not in employment_type.lower():

            item['Salary'] = 'Not specified'
        
        item['Source'] = ' https://www.monster.com.sg'

        item['Currency'] = 'SGD - S$'

        job_id = sel.css(".pLR-10:nth-child(4)::text").extract_first()

        if job_id is None:

            job_id = sel.css(".pLR-10:nth-child(3)::text").extract_first()
        
            job_id = job_id.split(":")

            if len(job_id)>1:

                job_id = job_id[1].strip()

            if job_id.isdigit():

                item['JobID'] = int(job_id)

        item['JobApplyLink'] = response.url

        posted_on = sel.css(".pLR-10:nth-child(1)::text").extract_first()

        if posted_on is not None:

            numeric_string = ''

            posted = posted_on.split(":")[1].strip().lower()

            posted = posted.split(" ")

            tod = datetime.datetime.now()

            if 'just' in posted or 'today' in posted or 'minutes' in posted or 'hours' in posted or 'hour' in posted:

                postedAt = tod

            else:

                if 'month' in posted:

                    if posted[0].strip().isdigit():

                        no_of_months = int(posted[0].strip())

                    else:

                        no_of_months = 1

                    months = 30 * no_of_months

                    numeric_string = str(months)

                    # d = datetime.timedelta(days=int(numeric_string))
                    # postedAt = tod - d
                else:

                    days = posted[0].replace("+", "").strip()

                    if not days.isdigit():

                        numeric_string = '1'

                    else:

                        numeric_string = days

                postedAt = tod - datetime.timedelta(days=int(numeric_string))

        else:
            tod = datetime.datetime.now()

            postedAt = tod

        time_in_date_time = str(postedAt).split(".")

        time_in_GMT = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.gmtime(time.mktime(time.strptime(time_in_date_time[0],
                                                                          "%Y-%m-%d %H:%M:%S"))))

        item['PostedAt'] = str(time_in_GMT)

        job_description = sel.css('div.job-description-content p.jd-text::text').getall()

        if job_description is None or len(job_description) ==0:

            job_description = sel.css('div.job-description-content li::text').getall()

            if job_description is None or len(job_description) ==0:

                job_description = sel.css('div.job-description-content p div::text').getall()

                if job_description is None or len(job_description) == 0:

                    job_description = sel.css('div.job-description-content span::text').getall()

                    if job_description is None or len(job_description) == 0:

                        job_description = sel.css('div.job-description-content div::text').getall()

                    if job_description is None or len(job_description) == 0:

                        job_description = ['-']

        item['JobDescription'] = ''.join(job_description)

        job_details = sel.css('.job-detail-list')

        for detail in job_details:

            key = detail.css('.dt-heading *::text').extract_first()

            value = detail.css('.dt-content *::text').extract()

            if 'Location' in key:

                item['Location'] = value[0]
            
            if 'Skills' in key:

                item['Skills'] = [i.split("\xa0")[0] for i in value if len(i.strip()) != 0]

            if 'Function' in 'key':

                item['JobFunction'] = value[0]

            else:

                item['JobFunction'] = 'IT'
            
            if 'Industry' in key:

                item['EmploymentIndustry'] = value[0].replace("\n", "").strip()

            if 'Posted' in key:

                item['PostedAt'] = value[0]

        yield item

        # # for count in range(0, jobsLen, 1):

        # #     if count == 1:
        # #         break
        # #     job_url = jobs[count].css('div.job-tittle h3 a::attr(href)').getall()

        # #     sels = response.request.get(job_url[0])

        # #     print(sels)

        #     # job_url[count] = jobs[count].css("div.card-body div.card-apply-content div.job-tittle a::attr(href)")

        #     # print("abc")

        #     # print("a", job_url[count])

        #     item = items.MonstersgItem()

        #     # print("ïtem",item)
        #     # print()

        #     item['JobTitle'] = jobs[count].css('div.job-tittle h3 *::text').extract_first().replace('\n', '').strip()

        #     item['EmployerName'] = jobs[count].css('span.company-name *::text').extract_first().replace('\n',
        #                                                                                                 '').strip()

        #     row = jobs[count].css('span.loc')

        #     keys = ['Location', 'Experience', 'Salary']

        #     for i in range(0, 3):

        #         if i < len(row):
        #             item[keys[i]] = row[i].css('small::text').extract_first().replace('\n', '').strip()

        #     item['JobURL'] = jobs[count].css('div.job-tittle a').xpath('@href').extract_first()

        #     item['Source'] = 'Monster'

        #     details = jobs[count].css("div.card-footer div.posted-update span::text").extract_first().strip()

        #     item['PostedAt'] = details.split(":")[1]

        #     # print("details", details.split(":")[1])

        #     # words = ['PostedAt', 'Views', 'JobID']

        #     # for i in range(0, 3):
        #     #     if i < len(details):
        #     # item['JobID'] = details[i].css('small::text').extract_first().replace('\n', '').strip()
        #     # print("item", item[words[i]])

        #     # etail = jobs[count].xpath('div/div[2]/div[1]/span[4]::text').getall()

        #     detail = sels.css(".pLR-10:nth-child(4)::text").extract_first()
        #     #
        #     job_id = sels.css(".pLR-10:nth-child(3)::text").extract_first()


        #     # item['JobID'] = detail.split(":")[1]


    def handle_error(self, failure):

        self.counter += 1

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

            # index = response.meta['index']

        # jobsLen = response.meta['jobsLen']

        # if index == jobsLen - 1 :

        #     print('I', index, jobsLen)

        #     if self.jobs_fetched < 200 :

        #         self.start = self.start + 50

        #         print('Start : ', self.start)

        #         yield SplashRequest(
        #                                 url='https://www.monsterindia.com/srp/results?start=' + str(self.start) + '&sort=1&limit=50&query=,',
        #                                 callback=self.parse,
        #                                 args={
        #                                     'wait' : 10
        #                                 }
        #                             )

# div = sel.css('#opt-desc-title')

# JobDescription = div.css('.job-desc *::text').extract()

# ul = response.css('.job-summary ul li')

# for li in ul :

#     key = li.css('label::text').extract_first()

#     value = li.css('span::text').extract_first()

# # -*- coding: utf-8 -*-
# import scrapy

# from scrapy_splash import SplashRequest
# from scrapy.selector import Selector
# from scrapy.http.request import Request
# from JobPostings import items

# class MonsterSpider(scrapy.Spider):

#     name = 'monster_1'

#     allowed_domains = ['monsterindia.com']

#     start_urls = ["https://www.monsterindia.com/search/all-countries-jobs"]
#     # start_urls = ['https://www.monsterindia.com/srp/results?sort=2&limit=25&query=,&searchId=033c7aca-55f9-402b-8408-77fb1a1e337f']
#     pages = 1

#     script = """
#         function main(splash, args)
#             splash:go(args.html_response)
#             splash:wait(0.5)
#             local button = splash:select('button.btn-next')
#             button:mouse_click()
#             splash:wait(3)
#             return { html : spalsh.html() }
#         end
#     """

#     def start_requests(self):
#         for url in self.start_urls:
#             yield SplashRequest(url=url, callback=self.parse)

#     def parse(self, response):

#         sel = Selector(response)
#         jobs = sel.xpath('//div[contains(@class, "job-apply-card")]')

#         self.pages = self.pages + 1

#         for job in jobs :

#             item = items.JobpostingsItem()

#             item['JobTitle'] = job.css('.job-tittle h3 *::text').extract_first().replace('\n', '').strip()
#             item['EmployerName'] = job.css('span.company-name *::text').extract_first().replace('\n', '').strip()

#             row = job.css('span.loc')

#             keys = ['Location', 'Experience', 'Salary']

#             for i in range(0, 3) :

#                 if i < len(row):
#                     item[keys[i]] = row[i].css('small::text').extract_first().replace('\n', '').strip()

#             skills = job.css('p.descrip-skills *::text').extract()
#             arr = []

#             for skill in skills :
#                 if len(skill.strip()) > 0:
#                     arr.append(skill.replace("u','", '').strip())

#             if len(arr) > 0 :
#                 item['JobQualifications'] = ' '.join(arr)

#             item['PostedAt'] = job.css('span.posted::text').extract_first().replace('\n','').strip()
#             item['JobURL'] = job.css('div.job-tittle a').xpath('@href').extract_first()

#             item['Source'] = 'Monster'

#             try :
#                 request = Request('https:' + item['JobURL'], callback=self.parse_results)
#                 request.meta['data'] = item
#                 yield request
#             except Exception, e :
#                 yield item

#         button = sel.css('.btn-next')

#         # if button :
#         #     if self.pages <= 2 :
#         #         yield SplashRequest(url=self.start_urls[0] + '-' + str(self.pages), callback=self.parse)

#     def parse_results(self, response) :

#         item = response.meta['data']

#         print('A')

#         JobDescription = response.xpath('//*[contains(@class, "card-panel job-description-content")]/text()').extract()

#         # print('A', JobDescription)

#         item['JobDescription'] = ' '.join(JobDescription)

#         keys = ['Industry', 'JobFunction', 'JobRole']

#         row = response.css('.job-detail-list')

#         for i in range(0, 3) :

#             if i < len(row) :
#                 item[keys[i]] = ' '.join(row[i].css('.dt-content *::text').extract()).replace('\n','').replace(' ', '').strip()

#         yield item


# skills = job.css('p.descrip-skills label *::text').extract()
# arr = []

# for skill in skills :
#     if len(skill.strip()) > 0:
#         arr.append(skill.replace("u','", '').strip())

# if len(arr) > 0 :
#     item['JobQualifications'] = ' '.join(arr)

# item['PostedAt'] = job.css('span.posted::text').extract_first().replace('\n','').strip()