import httpx
import asyncio

async def trigger():
    print("Triggering aggregation...")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post("http://localhost:8000/api/v1/articles/trigger")
            print(f"Status: {r.status_code}")
            print(f"Response: {r.json()}")
        except Exception as e:
            print(f"Failed to trigger aggregation: {e}")

if __name__ == "__main__":
    asyncio.run(trigger())
