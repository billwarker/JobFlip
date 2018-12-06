from config import Config
import pymongo

mongo_config = Config()
client = pymongo.MongoClient(mongo_config.MONGO_URI)

db = client[mongo_config.DB]

# post_id = posts.insert_one(test.total_scraped_jobs[0]).inserted_id
# print(post_id)

print(client.server_info())