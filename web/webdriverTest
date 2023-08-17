from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas
import re

PATH = ".\chromedriver.exe"
l = list()
o = {}

target_url = "https://www.glassdoor.com/Job/irvine-software-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,22.htm?radius=100"

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

        if ("software" in name.lower() and "intern" in name.lower()):
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

    
    
    l.append(o)
    o = {}


sorted_list = sorted(l, key=lambda x: x["name-of-company"])

df = pandas.DataFrame(sorted_list)
df.to_csv('jobtest.csv', index = False, encoding = "utf-8")
