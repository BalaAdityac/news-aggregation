import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

load_dotenv("Backend/.env")

async def test_mongo():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    print(f"Connecting to {mongo_url}...")
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
        info = await client.server_info()
        print("Connected to MongoDB successfully!")
        print(f"Server Info: {info['version']}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo())
