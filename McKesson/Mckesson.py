import http.client
import json
from csv import DictWriter
import time
import datetime
from collections import OrderedDict
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def fun(id=""):
    conn = http.client.HTTPSConnection("mckesson.wd3.myworkdayjobs.com")
    payload = ''
    headers = {
        'Accept': 'application/json,application/xml',
        'Cookie': 'PLAY_LANG=en-US; PLAY_SESSION=790025d8a312fea87faa7d17ae16a96c04789dbb-myhrabc_pSessionId=s84ntuup5fb9unq4s8o43gt2d7&instance=wd5prvps0004d; wday_vps_cookie=2938515978.61490.0000; timezoneOffset=-330'
    }
    j = 50
    page = 0
    job_list = []
    while (j <= 900):
        page = j / 50
        conn.request("GET", "Global/fs/searchPagination/318c8bb6f553100021d223d9780d30be/" + str(j), payload, headers)
        res = conn.getresponse()
        data = res.read()
        s = data.decode("utf-8")
        d = json.loads(s)
        urls = d['body']['children'][0]['children'][0]['listItems']
        for url in urls:
            job_spec = url["title"]["commandLink"]
            link = f'mckesson.wd3.myworkdayjobs.com{job_spec}'
            job_list.append(link)
        j += 50

    for url in job_list:
        dict = {}
        options = Options()
        options.add_argument("--headless")
        print("link = ", url)
        driver = webdriver.Chrome(options=options, executable_path=r'./chromedriver.exe')
        driver.get(url)
        driver.implicitly_wait(30)
        field_names = ["JobID", 'Title', 'PostedAt', 'Location', 'EmploymentType', "Description", "Source", "PAGE",
                       "ApplyLink"]
        body = driver.find_element_by_xpath('//*[@id="wd-PageContent-vbox"]/div')
        totalBody = body.find_elements_by_tag_name("li")
        li = []
        for k in totalBody:
            li.append(k.text)
        res = list(OrderedDict.fromkeys(li))
        re = res[:len(res) - 2]
        for i in re:
            if i == '':
                re.remove(i)
        dict['Title'] = re[0]
        dict['Location'] = re[1]
        dict['JobID'] = re[-1]
        dict['EmploymentType'] = re[-2]
        Posted = re[-3]
        tod = datetime.datetime.now()
        if 'today' in Posted:
            postedAt = tod
        elif 'yesterday' in Posted:
            postedAt = tod - datetime.timedelta(days=1)
        else:
            Posted = Posted.split(" ")
            days = Posted[1].replace("+", "").strip()
            if not days.isdigit():
                numeric_string = '1'
            else:
                numeric_string = days
            postedAt = tod - datetime.timedelta(days=int(numeric_string))
        time_in_date_time = str(postedAt).split(".")

        time_in_GMT = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.gmtime(time.mktime(time.strptime(time_in_date_time[0],
                                                                          "%Y-%m-%d %H:%M:%S"))))

        dict['PostedAt'] = str(time_in_GMT)
        for j in re:
            if len(j) >= 200:
                dict['JobDescription'] = j.replace('\n', '')
                break
        with open('mondetez.csv', 'a', encoding='utf-8', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            dictwriter_object.writerow(dict)
            f_object.close()
        driver.close()
fun()
