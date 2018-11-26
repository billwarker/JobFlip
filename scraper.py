import requests
import bs4
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import json
import pymongo
from app import conn, db

class Scraper:
    
    base_URL = "https://www.indeed.ca"

    def __init__(self, job, location):
        

        self.client = conn
        self.db = db

        self.date = datetime.today().strftime("%Y-%m-%d")
        self.job = job.replace(" ", "+").lower()
        self.location = location.replace(" ", "+").lower()
        self.URL = self.base_URL + "/jobs?q={}&l={}".format(self.job, self.location)
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
            next_href = pagination.find('a', href=True, text=self.pagination + 1).get("href")
            self.URL = self.base_URL + next_href
            self.pagination += 1

    def scrape(self, num_jobs=100):
        self.num_jobs = num_jobs
        print("""Scraping {} job results for "{}" """.format(num_jobs, self.job))
        while True:
            source_page = self.get_page(self.URL)
            found_jobs = self.get_jobs_on_page(source_page)
            for job in found_jobs:
                try:
                    if len(self.total_scraped_jobs) == num_jobs : break

                    job_data = {}
                    job_data["Title"] = self._extract_job_title(job)
                    job_data["Company"] = self._extract_job_employer(job)
                    if job_data["Company"] == "Indeed Prime": continue
                    job_data["Location"] = self._extract_job_location(job)
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
                except Exception: pass
                #time.sleep(0.5)
            
            if len(self.total_scraped_jobs) == num_jobs : break
            self.get_next_page(source_page)


    def write_json(self):
        self.json_file = "{}+{}+{}+{}.json".format(self.job, self.location, 
                                                   len(self.total_scraped_jobs), self.date)
        with open(self.json_file, 'w') as out_file:
            print("""Writing to "{}" """.format(self.json_file))
            json.dump(self.total_scraped_jobs, out_file)

    def write_to_mongo(self):
        print("Writing to MongoDB...")
        jobs = self.db.jobs
        #jobs = self.db["{}+{}".format(self.job, self.location)]
        jobs.insert_many(self.total_scraped_jobs)

if __name__ == "__main__":       
    test = Scraper("UX Designer", "Toronto")
    test.scrape(num_jobs=50)
    #test.write_json()
    test.write_to_mongo()