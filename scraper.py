import requests
import bs4
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import json
from pymongo import MongoClient
from config import Config

class Scraper:
    
    base_URL = "https://www.indeed.ca"

    def __init__(self, job, location, conn, db):
        

        self.client = conn
        self.db = db

        self.date = datetime.today().strftime("%Y-%m-%d")
        self.job = job.replace(" ", "+").lower()
        self.location = location.replace(" ", "+").lower()

        # &radius=0 will force a search for the exact city
        self.URL = self.base_URL + "/jobs?q={}&l={}&radius=0".format(self.job, self.location)
        self.pagination = 1
        self.total_scraped_jobs = []
        self.num_jobs = 100
        
    def get_page(self, URL):
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

    def get_jobs_on_page(self, soup):
        jobs = []
        for div in soup.find_all(name="div", attrs={"row"}):
            jobs.append(div)
        return jobs
    
    def _extract_job_title(self, job):
        for a in job.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
            if a is not None:
                return a["title"]

    def _extract_desc_href(self, job):
        for a in job.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
            if a is not None:
                return a["href"]

    def _extract_job_employer(self, job):
        company = job.find_all(name="span", attrs={"class":"company"})
        if len(company) > 0:
            for b in company:
                return b.text.strip()
        else:
            sec_try = job.find_all(name="span", attrs={"class":"result-link-source"})
            for span in sec_try:
                return span.text.strip()
    
    def _extract_job_location(self, job):
        spans = job.findAll("span", attrs={"class": "location"})
        if len(spans) > 0:
            return spans[0].text.strip()
        else:
            divs = job.findAll("div", attrs={"class": "location"})
            return divs[0].text.strip()

    def get_next_page(self, soup):
            pagination = soup.find("div", attrs={"class": "pagination"})
            try:
                next_href = pagination.find('a', href=True, text=self.pagination + 1).get("href")
                self.URL = self.base_URL + next_href
                self.pagination += 1
            except AttributeError:
                self.pagination = False

    def check_if_already_scraped(self, job_data):
        query_result = self.db.jobs.find({"$and": [{"Title": job_data["Title"]},
                                         {"Company": job_data["Company"]}]})
        return query_result.count()

    def scrape(self, num_jobs=100):
        self.num_jobs = num_jobs
        print(self.URL)
        print("""Scraping {} job results for "{}" in {} """.format(num_jobs, self.job, self.location))
        # pagination being a number is boolean equivalent to being true
        while self.pagination == True:
            source_page = self.get_page(self.URL)
            found_jobs = self.get_jobs_on_page(source_page)
            for job in found_jobs:
                try:
                    # check to see if we hit max jobs
                    if len(self.total_scraped_jobs) == num_jobs : break
                    # get job and company
                    job_data = {}
                    job_data["Title"] = self._extract_job_title(job)
                    job_data["Company"] = self._extract_job_employer(job)
                    
                    # if job in db or indeed prime, skip
                    if job_data["Company"] == "Indeed Prime" or \
                    self.check_if_already_scraped(job_data) == True: continue
                    
                    # location
                    job_data["Location"] = self._extract_job_location(job).split(",")[0]
                    
                    # get job description off href
                    desc_url = self.base_URL + self._extract_desc_href(job)
                    job_ad_page = self.get_page(desc_url)
                    page_text = job_ad_page.find("div", attrs={"class":"jobsearch-JobComponent-" + \
                                                            "description icl-u-xs-mt--md"}).findAll("li") 
                    desc = ""
                    for li in page_text:
                        desc += li.text + " "
                    job_data["Description"] = desc
                    self.total_scraped_jobs.append(job_data)
                    print("{}: {}".format(len(self.total_scraped_jobs), job_data['Title']))
                
                # if anything goes wrong just skip this job
                except Exception: continue
            
            if len(self.total_scraped_jobs) == num_jobs : break
            self.get_next_page(source_page)


    def write_json(self):
        self.json_file = "{}+{}+{}+{}.json".format(self.job, self.location, 
                                                   len(self.total_scraped_jobs), self.date)
        with open(self.json_file, 'w') as out_file:
            print("""Writing to "{}" """.format(self.json_file))
            json.dump(self.total_scraped_jobs, out_file)

    def write_to_mongo(self):
        job_count = len(self.total_scraped_jobs)
        if job_count > 0:
            print("Writing {} jobs to MongoDB...".format(job_count))
            self.db.jobs.insert_many(self.total_scraped_jobs)
        else:
            print("No new jobs to write!")

if __name__ == "__main__":

    db_config = Config()
    conn = MongoClient(db_config.MONGO_URI)
    db = conn[db_config.DB]
    test = Scraper("Chef", "Toronto", conn, db)
    test.scrape(num_jobs=50)
    test.write_to_mongo()