from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    with webdriver.Chrome() as driver:
        driver.get(target_url)

        driver.maximize_window()
        time.sleep(2)

        allJobsContainer = driver.find_element(By.CLASS_NAME, 'exy0tjh5')
        
        allJobs = allJobsContainer.find_elements(By.TAG_NAME, 'li')

        for job in allJobs:
            job_source = job.get_attribute("outerHTML")

            job_soup = BeautifulSoup(job_source, "html.parser")

            try:
                name = job_soup.find("div", {"class":"job-search-gx72iw"}).text
                name = re.sub(r'[^a-zA-Z\s]', '', name)
                o["name-of-company"]=name
            except:
                o["name-of-company"]=None

            try:
                name = job_soup.find("div",{"class":"job-title mt-xsm"}).text
                name = re.sub(r',', '', name)

                lower = name.lower()

                if (("software" in lower or "develop" in lower) and "intern" in name.lower()):
                    o["name-of-job"]=name
                else:
                    continue
            except:
                o["name-of-job"]=None

            try:
                location = job_soup.find("div",{"class":"location mt-xxsm"}).text
                location = re.sub(r',', '', location)
                o["location"]=location
            except:
                o["location"]=None

            try:
                salary = job_soup.find("div",{"class":"salary-estimate"}).text
                salary = re.sub(r',','', salary)
                o["salary"]=salary
            except:
                o["salary"]=None

            try:
                o["date"] = job_soup.find("div",{"class":"listing-age"}).text
            except:
                o["date"]=None

            job.click()

            extended_description = driver.find_element(By.CLASS_NAME, 'css-1d88wr9')

            driver.implicitly_wait(2)

            description_source = extended_description.get_attribute("outerHTML")

            description_soup = BeautifulSoup(description_source, "html.parser")

            try:
                app_link_element = description_soup.find("a", {"class": "css-akpsfi"})
                o["application-link"] = app_link_element.get("href")
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
