from urllib import response
import joblib
import json
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
from dotenv import load_dotenv
import os
import logging; logger = logging.getLogger(__name__)

def search_for_articles(query: str, top_k: int = 5, alpha: float = 0.5):
    # Load environment variables
    load_dotenv()

    # Load the BM25 model
    bm25 = joblib.load('bm25_model.joblib')

    # Load the embedding model configuration
    with open('embedding_config.json', 'r') as f:
        embedding_config = json.load(f)

    # Update the API key from the environment variable
    embedding_config['api_key'] = os.getenv('OPENAI_API_KEY')

    embedding_client = OpenAIEmbeddings(**embedding_config)

    # Load the Pinecone configuration
    with open('pinecone_config.json', 'r') as f:
        pinecone_config = json.load(f)

    # Update the API key from the environment variable
    pinecone_config['api_key'] = os.getenv('PINECONE_API_KEY')

    pc = Pinecone(api_key=pinecone_config['api_key'])
    pinecone_index = pc.Index(pinecone_config['index_name'])

    def convert_string_query_to_vectors(query: str):
        dense_vector = embedding_client.embed_query(query)
        sparse_vector = bm25.encode_queries(query)

        return {
            "dense": dense_vector,
            "sparse": sparse_vector
        }

    def hybrid_scale(dense, sparse, alpha: float):
        if alpha < 0 or alpha > 1:
            raise ValueError("Alpha must be between 0 and 1")
        hsparse = {
            'indices': sparse['indices'],
            'values':  [v * (1 - alpha) for v in sparse['values']]
        }
        hdense = [v * alpha for v in dense]
        return hdense, hsparse

    query_vectors = convert_string_query_to_vectors(query)
    scaled_dense, scaled_sparse = hybrid_scale(
        query_vectors['dense'], 
        query_vectors['sparse'], 
        alpha
    )
    results = pinecone_index.query(
        vector=scaled_dense,
        sparse_vector=scaled_sparse,
        top_k=top_k,
        include_metadata=True
    )

    for match in results['matches']:
        response = (json.loads(match['metadata']["response"]))
        if type(response) == list:
            response = response[0]

        match['title'] = response.get('title', 'No Title Available')

    print_results(results, query, top_k)
    return results['matches']

def print_results(results, query, top_k):
    logging.info(f"Top {top_k} results for query: '{query}'")
    for match in results['matches']:
        logging.debug(f"ID: {match['id']}")
        logging.debug(f"Score: {match['score']}")
        logging.debug(f"Response: {match['metadata']['response'][:1000]}...")  # Print first 1000 characters of the response
        #title = response.get('title', 'No Title Available')
        logging.debug("---")

# Example usage
# if __name__ == "__main__":
#     search_query = "Find a Huntingtin protein interaction with ubiquitin and its role in protein degradation"
#     logging.info(f"Search Query: {search_query}")
#     search_for_articles(search_query)
