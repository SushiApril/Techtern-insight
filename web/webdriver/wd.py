from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from collections import OrderedDict
from pathlib import Path
import re
import sqlite3
import traceback

'''
PENDING TASKS

-Use WebDriverWait for going between pages - still needs improvement?? But seems to work now
'''

def setup_database():
    open('./web/jobs_temp.db', 'w')
    conn = sqlite3.connect('./web/jobs_temp.db') # Creates a new SQLite file named 'jobs_temp.db'
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

def scrape(target_url, loads=5):
    with webdriver.Chrome() as driver:
        driver.get(target_url)

        driver.maximize_window()

        removeModalCSS = '.gd-ui-modal, .ModalContainer, #LoginModal {display: none;}'
        
        #this is for scraping Glassdoor without logging in. Prvenet login popup
        removeModalJS = f'''
                         var scriptRemoveStyle = document.createElement("style");
                         scriptRemoveStyle.innerHTML = "{removeModalCSS}";
                         document.head.appendChild(scriptRemoveStyle);
                         '''

        driver.execute_script(removeModalJS)

        wait1Min = WebDriverWait(driver, 60)

        def button_found(buttonContainer):
            try:
                button = buttonContainer.find_element(By.CLASS_NAME, 'button_Button__meEg5')

                return button.get_attribute("data-loading") == "false"
            except NoSuchElementException:
                return False

        for _ in range(loads - 1):
            buttonContainer = wait1Min.until(EC.presence_of_element_located((By.CLASS_NAME, "JobsList_buttonWrapper__haBp5")))

            waitForButton = WebDriverWait(buttonContainer, 60)

            waitForButton.until(button_found)

            loadMoreButton = buttonContainer.find_element(By.CLASS_NAME, 'button_Button__meEg5')

            loadMoreButton.click()

        resp = driver.find_element(By.CLASS_NAME, "JobsList_jobsList__Ey2Vo")

        respSource = resp.get_attribute("innerHTML")

        soup = BeautifulSoup(respSource, "html.parser")

        # BS
        allJobs = soup.find_all("li")
        # Selenium
        jobLinkElements = driver.find_elements(By.CLASS_NAME, "jobCard")

        button_has_link = lambda button: button.get_attribute("data-job-url")

        for job, jobLink in zip(allJobs, jobLinkElements):
            o = OrderedDict()

            try:
                try:
                    name = job.find("div",{"class":"css-8wag7x"}).text
                except:
                    name = job.find("div",{"class":"css-1bgdn7m"}).text

                try:
                    rating = job.find("span",{"class":"css-rnnx2x"}).text
                    name = name.replace(rating, "")
                except:
                    pass

                o["name-of-company"]=name.title()
            except:
                o["name-of-company"]=None

            try:
                name = job.find("a",{"class":"css-1nh9iuj"}).text
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
                    numDays = int(date[:-1]) + 1
                elif date == '24h':
                    numDays = 1
                elif date == '30d+':
                    numDays = 32
                else:
                    numDays = None

                o["date"]=numDays
            except:
                o["date"]=None

            jobLink.click()

            try:
                try:
                    appLinkElement = driver.find_element(By.CSS_SELECTOR, '[data-easy-apply="false"]')

                    waitForLink = WebDriverWait(appLinkElement, 60)

                    waitForLink.until(button_has_link)

                    linkPath = appLinkElement.get_attribute("data-job-url")
                except:
                    appLinkElement = job.find("a",{"class":"css-1nh9iuj"})
                    linkPath = appLinkElement.get('href')

                o["application-link"] = "https://www.glassdoor.com" + linkPath
            except:
                o["application-link"] = None

            insert_into_db(tuple(o.values()))

def insert_into_db(position):
    conn = sqlite3.connect('./web/jobs_temp.db')
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

def get_data():
    PATH = ".\chromedriver.exe"
    setup_database()
    _home = "https://www.glassdoor.com/Job/software-intern-jobs-SRCH_KO0,15.htm"
    page_8 = "https://www.glassdoor.com/Job/software-intern-jobs-SRCH_KO0,15_IP10.htm?includeNoSalaryJobs=true"
    targetUrl = [_home]
    try:
        for url in targetUrl:
            scrape(url,30)
    except Exception as err:
        print(traceback.format_exc())

    with sqlite3.connect('./web/jobs_temp.db') as conn:
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
            
    db_for_website = Path("./web/jobs.db")
    temp_db = Path("./web/jobs_temp.db")

    with temp_db.open("rb") as src:
        content = src.read()

    with db_for_website.open("wb") as dest:
        dest.write(content)