import os
from supabase import create_client, Client
from dotenv import load_dotenv

def check_supabase():
    # Try different .env locations
    dirs = [
        "c:/Users/LENOVO/OneDrive/Desktop/news aggregation/AI-Integration",
        "c:/Users/LENOVO/OneDrive/Desktop/news aggregation/Backend",
        "c:/Users/LENOVO/OneDrive/Desktop/news aggregation"
    ]
    
    for d in dirs:
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            print(f"Loading env from {env_path}")
            load_dotenv(env_path, override=True)
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if url and key:
                try:
                    supabase: Client = create_client(url, key)
                    res = supabase.table("articles").select("id", count="exact").limit(1).execute()
                    print(f"Total articles in Supabase: {res.count if hasattr(res, 'count') else 'unknown'}")
                    
                    # Check users
                    res_u = supabase.table("users").select("id", count="exact").limit(1).execute()
                    print(f"Total users in Supabase: {res_u.count if hasattr(res_u, 'count') else 'unknown'}")
                    
                    return
                except Exception as e:
                    print(f"Error connecting to Supabase with keys from {d}: {e}")

if __name__ == "__main__":
    check_supabase()
