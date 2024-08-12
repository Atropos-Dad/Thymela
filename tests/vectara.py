# import json
# import requests
# from typing import List, Dict

# # Vectara API configuration
# CUSTOMER_ID = "3280872075"
# CORPUS_ID = "2"
# API_KEY = "zut_w44ii_8CV2bdSc2IxtdvpnpL7q4NaGVlx9-Lgw"

# # API endpoints
# INDEX_URL = "https://api.vectara.io/v1/index"
# QUERY_URL = "https://api.vectara.io/v1/query"

# def load_studies(file_path: str) -> List[Dict]:
#     with open(file_path, 'r') as f:
#         studies = json.load(f)
#     return studies

# def index_studies(studies: List[Dict]):
#     url = INDEX_URL
#     headers = {
#         "Content-Type": "application/json",
#         "customer-id": CUSTOMER_ID,
#         "x-api-key": API_KEY
#     }

#     for study in studies:
#         study_id = study.get("studyId", "No Study ID")
#         payload = {
#             "corpusId": CORPUS_ID,
#             "document": {
#                 "documentId": study_id,
#                 "title": study_id,  # Using studyId as the title since it's required
#                 "description": json.dumps(study)
#             }
#         }
#         response = requests.post(url, json=payload, headers=headers)
#         if response.status_code == 200:
#             print(f"Indexed study with ID: {study_id}")
#         else:
#             print(f"Error indexing study with ID: {study_id}. Status code: {response.status_code}, Response: {response.text}")

# def search_studies(query: str) -> List[Dict]:
#     url = QUERY_URL
#     headers = {
#         "Content-Type": "application/json",
#         "customer-id": CUSTOMER_ID,
#         "x-api-key": API_KEY
#     }
#     payload = {
#         "query": [
#             {
#                 "query": query,
#                 "start": 0,
#                 "numResults": 10,
#                 "corpusKey": [
#                     {
#                         "corpusId": CORPUS_ID
#                     }
#                 ]
#             }
#         ]
#     }
#     response = requests.post(url, json=payload, headers=headers)
#     if response.status_code == 200:
#         results = response.json()
#         return results.get('responseSet', [{}])[0].get('response', [])
#     else:
#         print(f"Error searching studies. Status code: {response.status_code}")
#         return []
    
# # Load studies from JSON file
# file_path = 'tests/mock_data/csvjson (1).json'  # Update this path to your JSON file
# studies = load_studies(file_path)

# # Index studies in Vectara
# index_studies(studies)

# # while True:
# #     query = input("Enter your search query (or 'quit' to exit): ")
# #     if query.lower() == 'quit':
# #         break

# #     results = search_studies(query)
# #     if results:
# #         print("\nSearch Results:")
# #         for i, result in enumerate(results, 1):
# #             print(f"\n{i}. {result['text']}")
# #     else:
# #         print("No results found.")

import json
from typing import Dict, List
import requests


CUSTOMER_ID = "1724835199"  
CORPUS_ID = "3"
API_KEY = "zut_Zs7lf4Pd6mUFvfrtaD1MYBgt86-HtzYoTOqqnA"  
INDEX_URL = "https://api.vectara.io/v1/index"
QUERY_URL = "https://api.vectara.io/v1/query"

def index_document(item: dict, doc_id: str) -> dict:
    """
    Index a single document in Vectara.
    """
    # Flatten the nested structure
    flat_item = {}
    for key, value in item.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_item[f"{key}_{sub_key}"] = sub_value
        elif isinstance(value, list):
            flat_item[key] = ", ".join(map(str, value))
        else:
            flat_item[key] = value

    payload = {
        "customer_id": CUSTOMER_ID,
        "corpus_id": CORPUS_ID,
        "document": {
            "document_id": doc_id,
            "title": item.get('title', f"Study {doc_id}"),
            "metadata_json": json.dumps(flat_item),
            "section": [
                {
                    "text": "\n".join([f"{k}: {v}" for k, v in flat_item.items() if isinstance(v, (str, int, float))])
                }
            ]
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "customer-id": CUSTOMER_ID,
        "x-api-key": API_KEY
    }
    response = requests.post(INDEX_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Error indexing document: {response.text}")
    return response.json()

def index_json(json_file_path: str, limit: int = 120):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Check if data is a list
    if isinstance(data, list):
        studies = data
    else:
        # If it's a dictionary, navigate to the correct array
        studies = data.get('studies', [])

    for i, item in enumerate(studies):
        if i >= limit:
            break
        result = index_document(item, item['studyId'])
        if 'status' in result and result['status'].get('code') == 'OK':
            print(f"Successfully indexed document {i}")
        else:
            print(f"Failed to index document {i}: {result}")



def search_studies(query: str) -> List[Dict]:
    """
    Search for studies based on a query string.
    """
    headers = {
        "Content-Type": "application/json",
        "customer-id": CUSTOMER_ID,
        "x-api-key": API_KEY
    }
    payload = {
        "query": [
            {
                "query": query,
                "start": 0,
                "numResults": 10,
                "corpusKey": [
                    {
                        "corpusId": CORPUS_ID
                    }
                ]
            }
        ]
    }
    response = requests.post(QUERY_URL, json=payload, headers=headers)
    if response.status_code == 200:
        results = response.json()
        return results.get('responseSet', [{}])[0].get('response', [])
    else:
        print(f"Error searching studies. Status code: {response.status_code}")
        return []

#index_json("tests/mock_data/csvjson (1).json")




while True:
    query = input("Enter your search query (or 'quit' to exit): ")
    if query.lower() == 'quit':
        break

    results = search_studies(query)
    if results:
        print("\nSearch Results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['text']}")
    else:
        print("No results found.")