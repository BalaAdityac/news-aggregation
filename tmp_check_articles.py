import httpx
import asyncio

async def check():
    print("Checking article list...")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get("http://localhost:8000/api/v1/articles/")
            print(f"Status: {r.status_code}")
            data = r.json()
            print(f"Total articles: {data.get('total')}")
            if data.get('items'):
                print("Latest article:", data['items'][0]['title'])
        except Exception as e:
            print(f"Failed to fetch articles: {e}")

if __name__ == "__main__":
    asyncio.run(check())
