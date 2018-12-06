# JobFlip

JobFlip turns the job search on its head by showing you the most common words and phrases that appear in listings for a particular kind of job. When writing a resume or cover letter to apply to a company, the conventional wisdom is to use language that matches or at least answers to the qualifications and responsibilities being sought out in the listing. This is particularly important when applying to jobs online as many companies use screening systems that will filter out resumes that lack certain keywords.​ Job seekers who are unaware of these keywords run a high risk of having their applications rejected before they are even evaluated by a pair of human eyes.

JobFlip helps solve this problem by performing n-gram text analysis on job listings scraped from Indeed.ca. A n-gram is a contiguous sequence of length n words that is drawn from a text dataset. Often used in applications of computational linguistics such as machine translation, speech recognition, and spelling correction, n-grams are useful for chunking text data and counting the most common occurrences.​ 2​ By aggregating the text in different job listings for a certain role (e.g. truck driver, data analyst, chef) and running an n-gram analysis, JobFlip can find the strings of phrases and keywords that are most commonly associated with it. The resulting n-grams are visualized in the UI as a word cloud, where the size of each n-gram is dictated by its frequency in all of the related job listings.

## Quick Setup

1. Clone this repository.

2. Create a virtualenv with a version of Python 3 that is less than 3.7 (I used 3.6.7) and install the dependencies with the following command in your terminal: ```pip install -r requirements.txt```.

3. Create a file named config.py in the root folder and create the following class with your own credentials for a Mongo URI and MongoDB Database (the other credentials can stay the same):

```python
class Config:
    MONGO_URI = "mongodb+srv://will:!xXcq!m74B2xFdv@jobflip-6bgnt.mongodb.net/test?"
    DB = "test_database"
    SECRET_KEY = 'yeet'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

3. Open a second terminal window and start a local Redis server. If you don't have Redis installed on your computer, it can be downloaded from this [link.](https://redis.io/download)

4. Open a third terminal window. Activate the virtualenv and navigate to the JobFlip directory, then start a Celery worker with the following command ```app.celery --loglevel=info```.

5. Start the Flask application on your original terminal window: ```python app.py```