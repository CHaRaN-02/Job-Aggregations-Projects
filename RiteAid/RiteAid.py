import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import traceback
from urllib.parse import urljoin
from selenium.webdriver.chrome.options import Options
from csv import DictWriter

def JobPosting(url,page_no):
    # if page == limit:
    #     return
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options, executable_path=r'./chromedriver.exe')

    driver.get(url)
    page_no += 1
    time.sleep(1)
    # driver.implicitly_wait(10)
    field_names = ["JobID", 'Title', 'Location', 'EmploymentIndustry', "JobDescription",
                   "Source", "EmployerName", "ApplyLink", "JobURL"]
    jobpostings_li = driver.find_elements_by_css_selector('div.job-results-container > search-job-cards > mat-accordion > mat-expansion-panel.mat-expansion-panel')
    length = len(jobpostings_li)
    # print("len of li = ", length)

    if length != 0:
        for job in jobpostings_li:
            J_p_dict = {}

            industry = job.find_element_by_class_name('categories.label-value')
            # print("industry", industry)
            if industry:
                industry = (industry.text).strip()
                J_p_dict["EmploymentIndustry"] = industry

            job_info = job.find_element_by_tag_name('a')
            if job_info:

                J_p_dict["Source"] = "https://careers.riteaid.com/jobs?page=1"

                J_p_dict["EmployerName"] = "RiteAid"

                job_url = job_info.get_attribute('href')
                # print("Links", links)
                if job_url:
                    # print("Url", (job_url))
                    J_p_dict["JobURL"] = job_url

                    options = Options()
                    options.add_argument("start-maximized")
                    options.add_argument("--headless")
                    options.add_argument("--log-level=3")
                    driver_1 = webdriver.Chrome(options=options, executable_path=r'./chromedriver.exe')
                    driver_1.get(job_url)
                    time.sleep(1)
                    # driver_1.implicitly_wait(10)
                    try:
                        location = driver_1.find_element_by_class_name('job-locations-wrap.meta-data-option').text
                        # print('location', location)
                        if location:
                            # print('Location', location.strip())
                            J_p_dict["Location"] = location.strip()

                        description = driver_1.find_element_by_class_name('main-description-body').text
                        # print(description)
                        if description:
                            J_p_dict['JobDescription'] = description
                        # except NoSuchElementException as e:
                        #     continue
                        applyLink_elem = driver_1.find_element_by_id('link-apply')
                        applyLink = applyLink_elem.get_attribute('href')
                        # print('ApplyLink', applyLink)
                        if applyLink:
                            J_p_dict["ApplyLink"] = applyLink
                        driver_1.close()
                    except NoSuchElementException as e:
                        continue

                title_id = job_info.get_attribute('aria-label')
                if title_id:
                    title_id = title_id.rsplit(' ', 1)
                    title = title_id[0]
                    # print("title", title)
                    id = title_id[1]
                    # print('id', id)
                    J_p_dict["JobID"] = id
                    J_p_dict["Title"] = title

            with open('RiteAid.csv', 'a', encoding='utf-8', newline='') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                dictwriter_object.writerow(J_p_dict)
                f_object.close()
        next_page_url = 'https://careers.riteaid.com/jobs?page={}'.format(page_no)
        # print("****************************************", next_page_url)
        driver.close()
        JobPosting(next_page_url, page_no)
    else:
        return
url = 'https://careers.riteaid.com/jobs?page=1'
page_no = 1
JobPosting(url, page_no)



































































