from config import Config
import pymongo

mongo_config = Config()
client = pymongo.MongoClient(mongo_config.MONGO_URI)

db = client[mongo_config.DB]

# post_id = posts.insert_one(test.total_scraped_jobs[0]).inserted_id
# print(post_id)

job_query = "Data Scientist"
location_query = "Toronto"

job_results = db.jobs.find({"$and": [{"$text": {"$search": job_query, "$caseSensitive": False}},
                                        {"Location": location_query}]})

print(job_results.count())