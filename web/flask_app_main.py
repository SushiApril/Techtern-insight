from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datasite')
def datasite():
    with sqlite3.connect('web/jobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name_of_company, name_of_job, location, salary, date, application_link FROM jobs')

        def jobsGenerator():
            while job := cursor.fetchone():
                yield enumerate(job)

        return render_template('datasite.html', jobs=jobsGenerator())

if __name__ == '__main__':
    app.run()