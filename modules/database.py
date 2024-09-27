# modules/database.py - handles all database interactions

import os
from supabase import Client, create_client


class Database:
    def __init__(self):
        self.client = create_client(
            os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
        )

    def get_row(self, table_name, id):
        try:
            return self.client.table(table_name).select("data").eq("id", id).execute()
        except Exception as e:
            return -1

    def update_row(self, table_name, id, data):
        try:
            self.client.table(table_name).update({"data": data}).eq("id", id).execute()
            return 0
        except Exception as e:
            return -1
