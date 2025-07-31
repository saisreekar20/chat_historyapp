import csv
from azure.cosmos import CosmosClient
from datetime import datetime
import os
from dotenv import load_dotenv
import re 
load_dotenv()
# --- CONFIG ---
COSMOS_ENDPOINT = os.getenv("cosmos_end_point")
COSMOS_KEY = os.getenv("cosmos_key")
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database_name = "chatbot_sessions"
container_name = "chat_history"
# session_prefix = "4dd180b8a92a4b1785715d0de26c5a01-340b"
output_csv = "session_chat_export.csv"


    



# --- CONNECT ---
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)
 
# --- GET ALL DOCUMENTS THEN FILTER IN PYTHON ---
query = """
SELECT * FROM c
WHERE c.session_id LIKE @prefix
"""
def simp(user_id : str,app_name:str):
    cleaned_user_id = re.sub(r"-", "", user_id)
    session_prefix = cleaned_user_id + "-" + app_name  
    params = [{"name": "@prefix", "value": f"{session_prefix}-%"}]
    
    print(session_prefix)
    try:
        print("Querying Cosmos DB for all matching documents...")
        results = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        print(f"Found {len(results)} documents.")
    
        # for doc in results:
        #     print(doc.get("type"), "→", doc.get("content"), doc.get("sql_result"))
        import json
    
        print(json.dumps(results, indent=2))
    
    
    
        if results:
            # --- SORT ALL DOCUMENTS CHRONOLOGICALLY ---
            # We sort by the '_ts' (Unix timestamp) field, which is the most
            # reliable way to ensure the messages are in the correct order.
            print("Sorting documents by timestamp...")
            results.sort(key=lambda x: x.get('_ts', 0))
    
            # --- DYNAMICALLY DETERMINE CSV HEADERS ---
            # This automatically finds all possible fields from all messages
            # to ensure no data is lost in the export.
            all_fieldnames = set()
            for item in results:
                all_fieldnames.update(item.keys())
        
            # For better readability, we can define a preferred order for key columns
            preferred_order = [
                'session_id', 'id', '_ts', 'type', 'content', 'sql_query',
                'sql_query_summary', 'sql_result', 'error'
            ]
            # Append the rest of the columns alphabetically
            remaining_fields = sorted([field for field in all_fieldnames if field not in preferred_order])
            ordered_fieldnames = preferred_order + remaining_fields
    
            # --- EXPORT TO CSV ---
            print(f"Exporting all documents to {output_csv}...")
            with open(output_csv, "w", newline='', encoding='utf-8') as f:
                # DictWriter is used because messages may have different fields
                # (e.g., 'human' type messages won't have 'sql_query').
                writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
                writer.writeheader()
                writer.writerows(results)
    
            print(f"Successfully exported {len(results)} messages to {output_csv}")
            return results
        else:
            print("No documents were found matching the specified prefix.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

    
