from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve MongoDB URI from the environment
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB using the URI
try:
    # Establish MongoDB connection
    client = MongoClient(MONGO_URI)
    db = client["ShopkeepersDB"]  # Replace with your database name
    shopkeepers_col = db["shopkeepers"]  # Replace with your collection name
    
    # Test if the collection is accessible by counting documents
    user_count = shopkeepers_col.count_documents({})
    
    if user_count >= 0:
        print("✅ MongoDB connection is working!")
        print(f"Number of documents in 'shopkeepers' collection: {user_count}")
        print(MONGO_URI)
    else:
        print("❌ Could not fetch documents from the collection.")
        
except Exception as e:
    print(f"Error: {e}")
