from dotenv import load_dotenv
import os

load_dotenv()
print("Supabase URL:", os.getenv("SUPABASE_URL"))
