import os
import json
from pymongo import MongoClient
import nltk
from nltk.corpus import stopwords
from config import Config
from collections import Counter
#from app import conn, db

mongo_config = Config()
conn = MongoClient(mongo_config.MONGO_URI)
db = conn[mongo_config.DB]

stop_list = stopwords.words()

def find_relevant_jobs(job_query, location_query):
    db.jobs.create_index([('Title', 'text')])
    job_results = db.jobs.find({"$and": [{"$text": {"$search": job_query, "$caseSensitive": False}},
                                         {"Location": location_query}]})
    matches = job_results.count()
    return job_results, matches

def get_job_descriptions(job_results):
    descriptions = []
    for job in job_results:
        descriptions.append(job["Description"])
    return descriptions

# def get_n_grams_counts(descriptions, n):
#     n_grams = []
#     for desc in descriptions:
#         grams = nltk.ngrams(desc.split(), n)
#         for g in grams:
#             count = count_stop_words(g, 2)
#             if count >= 2:
#                 continue
#             else:
#                 phrase = ""
#                 for word in g:
#                     phrase += (word + " ")
#                 n_grams.append(phrase[:-1])
#     n_gram_counts = Counter(n_grams).most_common(100)
#     return n_gram_counts

def get_n_grams_counts(descriptions, n):
    n_grams = []
    for desc in descriptions:
        grams = nltk.ngrams(desc.split(), n)
        for g in grams:
            phrase=""
            for word in g:
                phrase += (word + " ")
            n_grams.append(phrase[:-1])
    n_gram_counts = Counter(n_grams).most_common(100)
    return n_gram_counts

def count_stop_words(g, threshold):
    stop_count = 0
    for word in g:
        if word in stop_list:
            stop_count +=1
    return stop_count



def convert_to_json_list(n_gram_counts):
    json_list = []
    for each in n_gram_counts:
        json = {"text": each[0], "size": each[1]}
        json_list.append(json)
    return json_list

def get_words(job_title, location, n_grams, n_words):
    results, job_matches = find_relevant_jobs(job_title, location)
    job_descriptions = get_job_descriptions(results)
    grams = get_n_grams_counts(job_descriptions, n_grams)
    word_list = convert_to_json_list(grams[:n_words])
    return word_list, job_matches


if __name__ == "__main__":
    job_results, num_matches = find_relevant_jobs('data scientist', "Toronto, ON")
    words = get_job_descriptions(job_results)
    grams = get_n_grams_counts(words, 3)
    listy = convert_to_json_list(grams)
