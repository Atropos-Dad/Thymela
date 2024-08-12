import json
import requests
from typing import List, Dict, Any

# Vectara API configuration
CUSTOMER_ID = "1724835199"
CORPUS_ID = "3"
API_KEY = "zut_w44ii_8CV2bdSc2IxtdvpnpL7q4NaGVlx9-Lgw"

# API endpoints
INDEX_URL = "https://api.vectara.io/v1/index"
QUERY_URL = "https://api.vectara.io/v1/query"

def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, ', '.join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)

def prepare_document(article: Dict[str, Any]) -> str:
    """
    Prepare a text representation of the article for indexing.
    """
    flat_article = flatten_dict(article)
    sections = [f"{k}: {v}" for k, v in flat_article.items() if v]
    return "\n".join(sections)

def index_document(article: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
    """
    Index a single document in Vectara.
    """
    response = article.get('response', {})
    
    # Debugging: Print the type and content of 'response'
    if not isinstance(response, dict):
        print(f"Unexpected response type: {type(response)}. Content: {response}")
    
    payload = {
        "customer_id": CUSTOMER_ID,
        "corpus_id": CORPUS_ID,
        "document": {
            "document_id": doc_id,
            "title": response.get('title', 'Untitled'),
            "metadata_json": json.dumps(article),
            "section": [{
                "text": prepare_document(article)
            }]
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "customer-id": CUSTOMER_ID,
        "x-api-key": API_KEY
    }
    response = requests.post(INDEX_URL, json=payload, headers=headers)
    
    # Debugging: Print response status and content
    if response.status_code == 200:
        print(f"Successfully indexed document {doc_id}: {response.json()}")
    else:
        print(f"Failed to index document {doc_id}. Status code: {response.status_code}, Response: {response.text}")
    
    return response.json()

def index_all_documents(articles: List[Dict[str, Any]]) -> None:
    """
    Index all documents in the provided list.
    """
    for i, article in enumerate(articles):
        # Debugging: Print the type of each article
        if not isinstance(article, dict):
            print(f"Skipping document {i} as it is not a dictionary. Content: {article}")
            continue
        
        # Ensure that 'response' is a dictionary
        response = article.get('response')
        if not isinstance(response, dict):
            print(f"Document {i} has 'response' of unexpected type: {type(response)}. Content: {response}")
            continue
        
        result = index_document(article, f"doc_{i}")
        print(f"Indexed document {i}: {result}")

def main():
    # Load the JSON data from the file
    with open("C:/Users/dylan/Downloads/csvjson (1).json", "r") as f:
        articles = json.load(f)
    
    # Ensure articles is a list
    if not isinstance(articles, list):
        print("Error: JSON data is not a list of articles.")
        return
    
    # Print the structure of the first few articles for debugging
    print("Sample article structure:")
    for i, article in enumerate(articles[:3]):
        print(f"Article {i}: {type(article)}")
        if isinstance(article, dict):
            print(f"Article {i} content: {article}")
    
    # Index all documents
    index_all_documents(articles)

if __name__ == "__main__":
    main()
