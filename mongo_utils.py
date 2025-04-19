# mongo_utils.py
from pymongo import MongoClient

# Replace with your actual MongoDB URI
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["ShopkeepersDB"]
shopkeepers_col = db["shopkeepers"]
