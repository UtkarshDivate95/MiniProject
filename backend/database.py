"""
MongoDB Atlas Database Connection Module
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from datetime import datetime
from bson import ObjectId
import os

# MongoDB Atlas connection string
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://02fe23bcs158_db_user:6vWzEU54ZxFs2M0j@cluster0.hjk73g2.mongodb.net/?appName=Cluster0"
)

DATABASE_NAME = "resume_ats_analyzer"
COLLECTION_NAME = "analysis_history"

# Global database client
client = None
db = None
collection = None


async def connect_to_mongodb():
    """Initialize MongoDB connection."""
    global client, db, collection
    try:
        client = AsyncIOMotorClient(MONGODB_URI, server_api=ServerApi('1'))
        # Verify connection
        await client.admin.command('ping')
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        print("✅ Successfully connected to MongoDB Atlas!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False


async def close_mongodb_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")


async def save_analysis(analysis_data: dict) -> str:
    """
    Save a resume analysis to MongoDB.
    Returns the inserted document ID.
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    # Add timestamp if not present
    if "created_at" not in analysis_data:
        analysis_data["created_at"] = datetime.utcnow()
    
    result = await collection.insert_one(analysis_data)
    return str(result.inserted_id)


async def get_analysis_history(limit: int = 10) -> list:
    """
    Get the most recent analyses from MongoDB.
    Returns list of analyses sorted by date (newest first).
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    cursor = collection.find().sort("created_at", -1).limit(limit)
    history = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        history.append(doc)
    return history


async def get_analysis_by_id(analysis_id: str) -> dict:
    """
    Get a specific analysis by its ID.
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    try:
        doc = await collection.find_one({"_id": ObjectId(analysis_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        return None


async def delete_analysis(analysis_id: str) -> bool:
    """
    Delete an analysis by its ID.
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def clear_all_history() -> int:
    """
    Clear all analysis history.
    Returns the number of deleted documents.
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    result = await collection.delete_many({})
    return result.deleted_count


async def get_total_analyses_count() -> int:
    """
    Get total count of analyses in the database.
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    return await collection.count_documents({})


async def get_analyses_stats() -> dict:
    """
    Get statistics about all analyses.
    """
    global collection
    if collection is None:
        raise Exception("Database not connected")
    
    total = await collection.count_documents({})
    
    # Get average scores using aggregation
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_overall_score": {"$avg": "$overall_score"},
                "avg_ats_score": {"$avg": "$ats_score"},
                "max_overall_score": {"$max": "$overall_score"},
                "min_overall_score": {"$min": "$overall_score"},
            }
        }
    ]
    
    stats = {"total_analyses": total}
    
    async for result in collection.aggregate(pipeline):
        stats.update({
            "avg_overall_score": round(result.get("avg_overall_score", 0), 1),
            "avg_ats_score": round(result.get("avg_ats_score", 0), 1),
            "max_overall_score": result.get("max_overall_score", 0),
            "min_overall_score": result.get("min_overall_score", 0),
        })
    
    return stats
