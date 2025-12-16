"""
Database Configuration - MongoDB with Beanie ODM
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

client: AsyncIOMotorClient = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM"""
    global client
    client = AsyncIOMotorClient(MONGODB_URL)
    
    from app.models.user import User
    from app.models.household import Household
    from app.models.alert import Alert
    
    await init_beanie(
        database=client.eeu_demand,
        document_models=[User, Household, Alert]
    )


async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
