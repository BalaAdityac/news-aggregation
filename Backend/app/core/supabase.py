from supabase import create_client, Client
from .config import settings

def get_supabase_client() -> Client:
    # Use the service_role key to bypass RLS on the server when needed
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("Supabase URL and Service Role Key are required.")
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
