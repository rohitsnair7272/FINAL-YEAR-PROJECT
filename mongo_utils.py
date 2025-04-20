# mongo_utils.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# Replace with your actual MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ShopkeepersDB"]
shopkeepers_col = db["shopkeepers"]
