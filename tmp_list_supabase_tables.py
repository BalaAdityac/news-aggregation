import os
from supabase import create_client, Client
from dotenv import load_dotenv

def list_tables():
    load_dotenv("c:/Users/LENOVO/OneDrive/Desktop/news aggregation/AI-Integration/.env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if url and key:
        try:
            supabase: Client = create_client(url, key)
            # Use rpc if possible, or just try common names
            tables = ["articles", "users", "newsletter_logs", "saved_articles", "profiles"]
            for t in tables:
                try:
                    res = supabase.table(t).select("id").limit(1).execute()
                    print(f"Table '{t}' exists.")
                except Exception as e:
                    if "PGRST205" in str(e):
                        print(f"Table '{t}' DOES NOT exist.")
                    else:
                        print(f"Table '{t}' error: {e}")
        except Exception as e:
            print(f"General error: {e}")

if __name__ == "__main__":
    list_tables()
