# mongo_utils.py
from pymongo import MongoClient
import os

# Replace with your actual MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ShopkeepersDB"]
shopkeepers_col = db["shopkeepers"]
