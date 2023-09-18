from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas
import re
import sqlite3

'''
PENDING TASKS

-Do not make scraper click a job when it does not need to be added
-Add easy apply URL as the job listing's own page
-Use WebDriverWait for going between pages???
'''

'''def remove_duplicate_dicts(input_list):
    unique_dicts = []
    for d in input_list:
        if d not in unique_dicts:
            unique_dicts.append(d)
    return unique_dicts'''

def setup_database():
    conn = sqlite3.connect('jobs.db') # Creates a new SQLite file named 'jobs.db'
    c = conn.cursor()
    
    # Create a new table
    c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        name_of_company TEXT,
        name_of_job TEXT,
        location TEXT,
        salary TEXT,
        date TEXT,
        application_link TEXT
    )
    ''')

    
    conn.commit()
    conn.close()


class Position(dict):
    COMPARISON_KEYS = ("name-of-company", "name-of-job", "location")

    def __eq__(self, other):
        try:
            for key in self.COMPARISON_KEYS:
                if self[key] != other[key]:
                    return False

            return True
        except KeyError:
            return False
        
    def __hash__(self):
        return hash(tuple(self[attr] for attr in self.COMPARISON_KEYS))
    
    def __lt__(self, other):
        self_name = self["name-of-company"]
        other_name = other["name-of-company"]

        if self_name == None:
            return False
        elif other_name == None:
            return True
        else:
            return self_name < other_name
        
    def to_tuple(self):
        return (self.get("name-of-company"), self.get("name-of-job"), self.get("location"), 
                self.get("salary"), self.get("date"), self.get("application-link"))
    




def scrape(target_url, max_pgs=100):
    with webdriver.Chrome() as driver:
        curr_pg = 1

        driver.get(target_url)

        driver.maximize_window()

        pagesLeft = True

        removeModalCSS = '#LoginModal {display: none;}'

        removeModalJS = f'''
                         var scriptRemoveStyle = document.createElement("style");
                         scriptRemoveStyle.innerHTML = "{removeModalCSS}";
                         document.head.appendChild(scriptRemoveStyle);
                         '''

        driver.execute_script(removeModalJS)

        while pagesLeft:
            time.sleep(2)

            resp = driver.find_element(By.CLASS_NAME, "css-152bcv1")

            respSource = resp.get_attribute("innerHTML")

            soup = BeautifulSoup(respSource, "html.parser")

            allJobsContainer = soup.find("ul", {"class":"css-7ry9k1"})

            allJobs = allJobsContainer.find_all("li")

            jobLinkElements = driver.find_elements(By.CLASS_NAME, "eigr9kq3")

            for job, jobLink in zip(allJobs, jobLinkElements):
                o = {}

                jobLink.click()

                try:
                    waitForElem = WebDriverWait(driver, 5)
                    name = waitForElem.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="employerName"]')))
                    name = name.text.split("\n")[0]
                    name = re.sub(r',', '', name)
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

                try:
                    appLink = driver.find_element(By.CSS_SELECTOR, '[data-easy-apply="false"]')

                    o["application-link"] = "https://www.glassdoor.com" + appLink.get_attribute("data-job-url")
                except:
                    o["application-link"] = None

                l.add(Position(o))

            nextButton = driver.find_element(By.CLASS_NAME, "nextButton")

            if nextButton.get_attribute("disabled") == None and curr_pg != max_pgs:
                nextButton.click()
                curr_pg += 1
            else:
                pagesLeft = False

def insert_into_db(position):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
<<<<<<< Updated upstream
    c.execute('''
    INSERT INTO jobs (name_of_company, name_of_job, location, salary, date, application_link)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', position.to_tuple())
    
    conn.commit()
=======
        conn.commit()
        print(position.to_tuple())
    except sqlite3.IntegrityError:
        #print("Duplicate entry detected!")
        pass
>>>>>>> Stashed changes
    conn.close()




def run():
    setup_database()

    PATH = ".\chromedriver.exe"

    target_url = ["https://www.glassdoor.com/Job/irvine-python-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,20.htm?radius=100","https://www.glassdoor.com/Job/irvine-software-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,22.htm?radius=100"]

    for url in target_url:
        scrape(url)


    sorted_list = sorted(l) #, key=lambda x: '' if x["name-of-company"] == None else x["name-of-company"])

    for sl in l:
        insert_into_db(sl)
    df = pandas.DataFrame(sorted_list)
    df.to_csv('web/jobtest.csv', index = False, encoding = "utf-8")



if __name__=="__main__":
    PATH = ".\chromedriver.exe"
    l = set()
    setup_database()
    target_url = ["https://www.glassdoor.com/Job/irvine-python-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,20.htm?radius=100","https://www.glassdoor.com/Job/irvine-software-intern-jobs-SRCH_IL.0,6_IC1146798_KO7,22.htm?radius=100"]

    for url in target_url:
        scrape(url)


    sorted_list = sorted(l) #, key=lambda x: '' if x["name-of-company"] == None else x["name-of-company"])

    for sl in l:
        insert_into_db(sl)
    df = pandas.DataFrame(sorted_list)
    df.to_csv('web/jobtest.csv', index = False, encoding = "utf-8")