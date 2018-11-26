from scraper import Scraper
import pymongo

test = Scraper("construction", "Oshawa")
test.scrape(num_jobs=2)

client = pymongo.MongoClient("mongodb+srv://will:!xXcq!m74B2xFdv@jobflip-6bgnt.mongodb.net/test?")

db = client.test_database
posts = db.posts
# post_id = posts.insert_one(test.total_scraped_jobs[0]).inserted_id
# print(post_id)

print(posts.find_one())
