from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from random import random
import requests
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
        time.sleep(random())

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

        extendedDescriptionResponse = requests.get(extendedDescriptionLink, headers={
            "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
            "Accept-Encoding": "gzip, deflate, br", 
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7", 
            "Dnt": "1", 
            "Host": "glassdoor.com", 
            "Referer": target_url, 
            "Sec-Ch-Ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"", 
            "Sec-Ch-Ua-Mobile": "?0", 
            "Sec-Ch-Ua-Platform": "\"Windows\"", 
            "Sec-Fetch-Dest": "document", 
            "Sec-Fetch-Mode": "navigate", 
            "Sec-Fetch-Site": "cross-site", 
            "Sec-Fetch-User": "?1", 
            "Upgrade-Insecure-Requests": "1", 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36", 
            "X-Amzn-Trace-Id": "Root=1-64e83661-0ad85904753e7cc54d34580c",
        })

        extendedDescriptionSoup = BeautifulSoup(extendedDescriptionResponse.text, "html.parser")

        #x=extendedDescriptionResponse.text.index('data-easy-apply')
        print(extendedDescriptionResponse.text)

        try:
            appLinkElement = extendedDescriptionSoup.find("button", {"data-easy-apply": "false"})
            o["application-link"] = "https://www.glassdoor.com" + appLinkElement["data-job-url"]
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