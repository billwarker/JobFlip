from flask import Flask
from flask import render_template, redirect, request
from config import *

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import words as w
# from scraper import Scraper

from pymongo import MongoClient
from celery import Celery

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

conn = MongoClient(MONGO_URI)
db = conn[DB]

# @celery.task
# def scrape_job_data(job_query, location_query, num_jobs):
#     scraper = Scraper(job_query, location_query)
#     scraper.scrape(num_jobs=num_jobs)
#     scraper.write_to_mongo()

class SearchForm(FlaskForm):
    job_title = StringField("Job Title", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Search Jobs")

@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"]) 
def index():
    form = SearchForm()
    # if user does a search
    if form.validate_on_submit():
        job = form.job_title.data
        location = form.location.data
        try:
            word_freqs_js = w.get_words(job, 5, 50)
            max_freq = word_freqs_js[0]["size"]
            if max_freq < 10: max_freq = 10
            else: max_freq = 20
            return render_template("index.html", form=form,
                                                word_freqs=word_freqs_js,
                                                max_freq=max_freq)
        except IndexError:
            # scrape_job_data.apply_async(args=[job, location, 50])
            word_freqs_js = [{"text": "No Results", "size": 5}, {"text": "Searching Indeed.ca...", "size": 2}]
            max_freq = 5
            return render_template("index.html", form=form,
                                                word_freqs=word_freqs_js,
                                                max_freq=max_freq)

    # displaying the initial index page
    word_freqs_js = [{"text": "Search", "size": 5}, {"text": "for", "size": 5},
                    {"text": "a", "size": 5}, {"text": "job!", "size": 5}]
    max_freq = 4
    return render_template("index.html", form=form,
                                         word_freqs=word_freqs_js,
                                         max_freq=max_freq)

@app.route('/data')    
def data():
    jobs = db.jobs.find()
    return render_template("data.html", jobs=jobs)


if __name__ == "__main__":
    app.debug = True
    app.run()