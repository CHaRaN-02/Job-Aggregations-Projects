#Author : Sai Charan
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

def JobPosting(url,Offset):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options, executable_path=r'./chromedriver.exe') 
    driver.get(url)
    Offset += 25

    field_names = ["JobID", 'Title', 'Location', 'EmploymentIndustry', "JobDescription",
                   "Source",  "JobURL"]


    links = []
    elems = driver.find_elements_by_xpath("//a[@href]") 
    for elem in elems:

        job_urls = elem.get_attribute("href")
        links.append(job_urls)
         
    for job_url in links[14:26]:
        J_p_dict = {}
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        driver_1 = webdriver.Chrome(options=options, executable_path=r'./chromedriver.exe')
        driver_1.get(job_url)
        ############### Title ###############
        J_p_dict['Title'] = driver_1.find_elements_by_tag_name('h2')[0].text
        ############### Location ###############
        J_p_dict['Location'] = driver_1.find_element_by_class_name('fields-data_value').text
        ############### JobID ###############
        J_p_dict['JobID'] = driver_1.find_element_by_xpath('//*[@id="content"]/div/div[2]/div/div[2]/div[2]/div/div/ul/li[5]/div[2]').text
        ############### EmploymentIndustry ###############
        J_p_dict['EmploymentIndustry'] = driver_1.find_element_by_xpath('//*[@id="content"]/div/div[2]/div/div[2]/div[2]/div/div/ul/li[2]/div[2]').text
        ############### JobDescription ###############
        J_p_dict['JobDescription'] = driver_1.find_element_by_class_name('job_description').text
        ############### job_url ###############
        J_p_dict['JobURL'] = job_url
        J_p_dict['Source'] = 'Cisco'

        with open('Cisco.csv', 'a', encoding='utf-8', newline='') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                dictwriter_object.writerow(J_p_dict)
                f_object.close()
        next_page_url = 'https://jobs.cisco.com/jobs/SearchJobs/?source=Cisco+Jobs+Career+Site&tags=CDC+Browse+all+jobs+careers&projectOffset={}'.format(Offset)
        # print("****************************************", next_page_url)
        driver.close()
        JobPosting(next_page_url, Offset)
    else:
        return
url = 'https://jobs.cisco.com/jobs/SearchJobs/?source=Cisco+Jobs+Career+Site&tags=CDC+Browse+all+jobs+careers&projectOffset=0'
Offset = 0
JobPosting(url, Offset)


