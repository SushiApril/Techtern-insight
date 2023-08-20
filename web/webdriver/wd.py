from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas
import re

PATH = ".\chromedriver.exe"
l = list()

def remove_duplicate_dicts(input_list):
    unique_dicts = []
    for d in input_list:
        if d not in unique_dicts:
            unique_dicts.append(d)
    return unique_dicts

def scrape(target_url):
    o = {}
    driver = webdriver.Chrome()

    driver.get(target_url)

    driver.maximize_window()
    time.sleep(2)

    resp = driver.page_source

    driver.close()

    soup = BeautifulSoup(resp, "html.parser")

    allJobsContainer = soup.find("ul", {"class":"css-7ry9k1"})

    allJobs = allJobsContainer.find_all("li")


    for job in allJobs:
        try:
            name = job.find("div", {"class":"job-search-gx72iw"}).text
            name = re.sub(r'[^a-zA-Z\s]', '', name)
            o["name-of-company"]=name
        except:
            o["name-of-company"]=None

        try:
            name = job.find("div",{"class":"job-title mt-xsm"}).text
            name = re.sub(r',', '', name)

            lower = name.lower()

            if (("software" in lower or "develop" in lower) and "intern" in name.lower()):
                o["name-of-job"]=name
            else:
                continue
        except:
            o["name-of-job"]=None

        try:
            location = job.find("div",{"class":"location mt-xxsm"}).text
            location = re.sub(r',', '', location)
            o["location"]=location
        except:
            o["location"]=None

        try:
            salary = job.find("div",{"class":"salary-estimate"}).text
            salary = re.sub(r',','', salary)
            o["salary"]=salary
        except:
            o["salary"]=None

        try:
            o["date"] = job.find("div",{"class":"listing-age"}).text
        except:
            o["date"]=None

        extendedDescriptionLinkElement = job.find("a")

        extendedDescriptionLink = "https://www.glassdoor.com" + extendedDescriptionLinkElement["href"]

        extendedDescription = webdriver.Chrome()

        extendedDescription.get(extendedDescriptionLink)

        extendedDescriptionSource = extendedDescription.page_source
        '''x=extendedDescriptionSource.index('data-easy-apply')
        print(extendedDescriptionSource[x-150:x+250])'''

        extendedDescriptionSoup = BeautifulSoup(extendedDescriptionSource, "html.parser")

        try:
            appLinkElement = extendedDescriptionSoup.find("button", {"data-easy-apply": "false"})
            o["application-link"] = "https://www.glassdoor.com" + appLinkElement["data-job-url"]
            print(o["application-link"])
        except:
            o["application-link"] = None

        l.append(o)
        o = {}

target_url = ["https://www.glassdoor.com/Job/irvine-python-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,20.htm?radius=100","https://www.glassdoor.com/Job/irvine-software-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,22.htm?radius=100"]

for url in target_url:
    scrape(url)


l = remove_duplicate_dicts(l)

sorted_list = sorted(l, key=lambda x: x["name-of-company"])

df = pandas.DataFrame(sorted_list)
df.to_csv('jobtest.csv', index = False, encoding = "utf-8")