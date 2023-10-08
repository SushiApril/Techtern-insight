from flask import Flask, render_template
import pandas as pd
import sqlite3
from eda import *
from datetime import datetime, timedelta
import threading
from importlib.util import spec_from_file_location, module_from_spec

spec = spec_from_file_location("wd", "web\webdriver\wd.py")

wd = module_from_spec(spec)

spec.loader.exec_module(wd)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datasite')
def datasite():
    TODAY = datetime.today().date()

    with sqlite3.connect('web/jobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name_of_company, name_of_job, location, salary, date, application_link FROM jobs')

        def jobsGenerator():
            while job := cursor.fetchone():
                yield enumerate(job)

        return render_template('datasite.html', timedelta=timedelta, jobs=jobsGenerator(), today=TODAY)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stats')
def stats():
    df = pd.read_csv("https://raw.githubusercontent.com/SushiApril/Techtern-insight/rebuild-site-with-flask/jobs.csv")
    df = clean_data(df)

    avg_salary_distribution = plot_avg_salary_distribution(df)
    jobs_by_state = plot_jobs_by_state(df)
    top_cities_by_jobs = plot_top_cities_by_jobs(df)
    avg_salary_by_state = plot_avg_salary_by_state(df)
    salaries_by_state = plot_salaries_by_state(df)
    salary_density_by_state = plot_salary_density_by_state(df)
    salary_boxplot_by_state = plot_salary_boxplot_by_state(df)
    company_wise_job_postings = plot_company_wise_job_postings(df)

    return render_template("stats.html",  avg_salary_distribution=avg_salary_distribution,
                           jobs_by_state=jobs_by_state, top_cities_by_jobs=top_cities_by_jobs, avg_salary_by_state=avg_salary_by_state,
                           salaries_by_state=salaries_by_state, salary_density_by_state=salary_density_by_state, salary_boxplot_by_state=salary_boxplot_by_state, 
                           company_wise_job_postings=company_wise_job_postings)  

def run():
    app.run(port=5004)

def get_data_periodically():
    sched_time = 60 * (1 * 60 + 50)

    while True:
        now = datetime.now()

        seconds = 3600 * now.hour + now.minute * 60 + now.second

        timer_until_midnight = threading.Timer(sched_time - seconds, wd.get_data)

        timer_until_midnight.start()

        timer_until_midnight.join()

        sched_time = 86400

def main():
    application = threading.Thread(target=run)
    scrape = threading.Thread(target=get_data_periodically)

    application.start()
    scrape.start()

if __name__ == '__main__':
    main()
