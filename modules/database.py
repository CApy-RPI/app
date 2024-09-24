#modules.database.py - handles all database interactions (hosted on supagbase)

import os
from supabase import Client, create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

# TBI

