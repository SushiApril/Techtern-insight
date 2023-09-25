from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import sqlite3

'''
PENDING TASKS

-Add easy apply URL as the job listing's own page
-Use WebDriverWait for going between pages???
'''

def setup_database():
    open('./web/jobs.db', 'w')
    conn = sqlite3.connect('./web/jobs.db') # Creates a new SQLite file named 'jobs.db'
    c = conn.cursor()
    
    # Create a new table
    c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        name_of_company TEXT,
        name_of_job TEXT,
        location TEXT,
        salary TEXT,
        date INTEGER,
        application_link TEXT NOT NULL,
        UNIQUE(name_of_company, name_of_job, location)
    )
    ''')

    
    conn.commit()
    conn.close()

def scrape(target_url, maxPgs=5):
    with webdriver.Chrome() as driver:
        currPg = 1

        driver.get(target_url)

        driver.maximize_window()

        pagesLeft = True

        removeModalCSS = '#LoginModal {display: none;}'
        
        #this is for scraping glassdoor without logging in. Prvenet login popup
        removeModalJS = f'''
                         var scriptRemoveStyle = document.createElement("style");
                         scriptRemoveStyle.innerHTML = "{removeModalCSS}";
                         document.head.appendChild(scriptRemoveStyle);
                         '''

        driver.execute_script(removeModalJS)

        wait1Min = WebDriverWait(driver, 60)

        while pagesLeft:
            #checks if its the correct page to scrape
            def correctPage(driver):
                try:
                    pageNumElement = driver.find_element(By.CLASS_NAME, 'paginationFooter')
                    return f'Page {currPg}' in pageNumElement.text
                except NoSuchElementException:
                    return False

            wait1Min.until(correctPage)

            resp = driver.find_element(By.CLASS_NAME, "css-152bcv1")

            respSource = resp.get_attribute("innerHTML")

            soup = BeautifulSoup(respSource, "html.parser")

            # BS
            allJobsContainer = soup.find("ul", {"class":"css-7ry9k1"})
            # BS
            allJobs = allJobsContainer.find_all("li")
            # Selenium
            jobLinkElements = driver.find_elements(By.CLASS_NAME, "eigr9kq3")

            for job, jobLink in zip(allJobs, jobLinkElements):
                o = OrderedDict()

                try:
                    nameInfo = {}

                    for info, tag, classId in zip(('name', 'rating'), ('div', 'span'), ('8wag7x', 'rnnx2x')):
                        for idPrefix in ('css', 'job-search'):
                            try:
                                nameInfo[info] = job.find(tag,{"class":f"{idPrefix}-{classId}"}).text
                            except:
                                continue
                            else:
                                break

                    name = nameInfo['name'].replace(nameInfo['rating'], '')
                    o["name-of-company"]=name.title()
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
                    date = job.find("div",{"class":"listing-age"}).text

                    if date[-1] == 'd':
                        numDays = int(date[:-1])  
                    elif date == '24h':
                        numDays = 0
                    elif date == '30d+':
                        numDays = 31
                    else:
                        numDays = None

                    o["date"] = numDays
                except:
                    o["date"]=None

                jobLink.click()

                try:
                    try:
                        appLinkElement = driver.find_element(By.CSS_SELECTOR, '[data-easy-apply="false"]')
                        linkPath = appLinkElement.get_attribute("data-job-url")
                    except:
                        appLinkElement = job.find("a",{"class":"jobCard"})
                        linkPath = appLinkElement.get('href')

                    o["application-link"] = "https://www.glassdoor.com" + linkPath
                except:
                    o["application-link"] = None

                insert_into_db(tuple(o.values()))

            nextButton = driver.find_element(By.CLASS_NAME, "nextButton")

            if nextButton.get_attribute("disabled") == None and currPg != maxPgs:
                nextButton.click()
                currPg += 1
            else:
                pagesLeft = False

def insert_into_db(position):
    conn = sqlite3.connect('./web/jobs.db')
    c = conn.cursor()
    try:
        c.execute('''
        INSERT INTO jobs (name_of_company, name_of_job, location, salary, date, application_link)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', position)
    
        conn.commit()
        print(position)
    except sqlite3.IntegrityError as err:
        print("Duplicate entry detected - ", position, str(err))
    conn.close()

def main():
    PATH = ".\chromedriver.exe"
    setup_database()
    _home = "https://www.glassdoor.com/Job/software-intern-jobs-SRCH_KO0,15.htm"
    page_8 = "https://www.glassdoor.com/Job/software-intern-jobs-SRCH_KO0,15_IP10.htm?includeNoSalaryJobs=true"
    targetUrl = [_home]
    try:
        for url in targetUrl:
            scrape(url,30)
    except:
        print("An error happened")

    with sqlite3.connect('./web/jobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name_of_company, name_of_job, location, salary, date, application_link FROM jobs ORDER BY date ASC;')

        rows = cursor.fetchall()

        cursor.execute('DELETE FROM jobs')

        for row in rows:
            print(tuple(row))
            cursor.execute('''
                INSERT INTO jobs (name_of_company, name_of_job, location, salary, date, application_link)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', tuple(row))
            
if __name__=="__main__":
    main()