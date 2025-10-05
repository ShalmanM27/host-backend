from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

print("✅ MongoDB Atlas connected successfully!")

# Simple test function
def test_connection():
    try:
        # List collections
        collections = db.list_collection_names()
        print("Collections in DB:", collections)
        
        # Optional: Insert a test document
        test_doc = {"test_field": "Hello Atlas"}
        result = db.test_collection.insert_one(test_doc)
        print("Inserted document ID:", result.inserted_id)

        # Optional: Fetch the document back
        fetched = db.test_collection.find_one({"_id": result.inserted_id})
        print("Fetched document:", fetched)

        print("✅ MongoDB Atlas connection test successful!")

    except Exception as e:
        print("❌ MongoDB Atlas connection failed:", e)

# Run the test
if __name__ == "__main__":
    test_connection()
