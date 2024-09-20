#modules.database.py - handles all database interactions (hosted on supagbase)

import os
from supabase import Client, create_client

supabase_url = os.getenv("supabase_url")
supabase_key = os.getenv("supabase_key")

supabase = create_client(supabase_url, supabase_key)

# TBI

