from flask import Flask
from flask import render_template, redirect, request
from config import Config

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

import words as w
from scraper import Scraper

from pymongo import MongoClient
from celery import Celery

app = Flask(__name__)
app.config.from_object(Config)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

mongo_config = Config()
conn = MongoClient(mongo_config.MONGO_URI)
db = conn[mongo_config.DB]

@celery.task(bind=True)
def scrape_job_data(job_query, location_query, num_jobs):
    scraper = Scraper(job_query, location_query, conn, db)
    scraper.scrape(num_jobs=num_jobs)
    scraper.write_to_mongo()

class SearchForm(FlaskForm):
    job_title = StringField("Job Title", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    n_grams = IntegerField("N Grams", validators=[DataRequired()]) 
    submit = SubmitField("Search Jobs")

@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"]) 
def index():
    form = SearchForm()
    # if user does a search
    if form.validate_on_submit():
        job = form.job_title.data
        location = form.location.data
        n_grams = form.n_grams.data
        try:
            word_freqs_js = w.get_words(job, n_grams, 50)
            max_freq = word_freqs_js[0]["size"]
            print(max_freq)
            if max_freq < 10 and max_freq >= 5: max_freq = 10
            elif max_freq < 5: max_freq = 3
            else: max_freq = 20
            return render_template("index.html", form=form,
                                                word_freqs=word_freqs_js,
                                                max_freq=max_freq)
        except IndexError:
            scrape_job_data.apply_async(args=[job, location, 50])
            print("Looking for jobs...")
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