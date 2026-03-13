import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# Connect securely to the MongoDB container running in Docker
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["prothoton_hospital"]
consultations_collection = db["consultations"]

async def save_consultation_record(record_dict: dict) -> dict:
    """
    Saves the structured consultation record into MongoDB.
    Appends a timestamp to the record before insertion.
    """
    try:
        record_dict["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        # Insert the document
        result = await consultations_collection.insert_one(record_dict)
        
        # Ensure it returns clean JSON structure with stringified ObjectId
        record_dict["_id"] = str(result.inserted_id)
        return record_dict
    except Exception as e:
        print(f"MongoDB Insertion Error: {e}")
        return {"error": str(e)}
