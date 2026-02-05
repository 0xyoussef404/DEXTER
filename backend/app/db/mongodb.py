"""
MongoDB connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class MongoDB:
    """MongoDB connection manager"""
    
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGO_URL)
        cls.db = cls.client[settings.MONGO_DB_NAME]
    
    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
    
    @classmethod
    def get_collection(cls, name: str):
        """Get a collection from the database"""
        return cls.db[name]


# Initialize MongoDB
mongodb = MongoDB()
