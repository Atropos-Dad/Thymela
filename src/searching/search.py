import joblib
import json
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

def search_query_parser(query: str):
    needed_keywords = [word[1:-1] for word in query.split() if word.startswith('"') and word.endswith('"')]
    return needed_keywords, query

class ArticleSearcher:
    def __init__(self):
        load_dotenv()
        self.bm25 = joblib.load('bm25_model.joblib')
        
        with open('embedding_config.json', 'r') as f:
            embedding_config = json.load(f)
        embedding_config['api_key'] = os.getenv('OPENAI_API_KEY')
        self.embedding_client = OpenAIEmbeddings(**embedding_config)
        
        with open('pinecone_config.json', 'r') as f:
            pinecone_config = json.load(f)
        pinecone_config['api_key'] = os.getenv('PINECONE_API_KEY')
        pc = Pinecone(api_key=pinecone_config['api_key'])
        self.pinecone_index = pc.Index(pinecone_config['index_name'])

    def convert_string_query_to_vectors(self, query: str):
        dense_vector = self.embedding_client.embed_query(query)
        sparse_vector = self.bm25.encode_queries(query)
        return {
            "dense": dense_vector,
            "sparse": sparse_vector
        }

    @staticmethod
    def hybrid_scale(dense, sparse, alpha: float):
        if alpha < 0 or alpha > 1:
            raise ValueError("Alpha must be between 0 and 1")
        hsparse = {
            'indices': sparse['indices'],
            'values': [v * (1 - alpha) for v in sparse['values']]
        }
        hdense = [v * alpha for v in dense]
        return hdense, hsparse

    def search_for_articles(self, query: str, top_k: int = 5, alpha: float = 0.5):
        query_vectors = self.convert_string_query_to_vectors(query)
        scaled_dense, scaled_sparse = self.hybrid_scale(
            query_vectors['dense'],
            query_vectors['sparse'],
            alpha
        )
        results = self.pinecone_index.query(
            vector=scaled_dense,
            sparse_vector=scaled_sparse,
            top_k=top_k,
            include_metadata=True
        )

        for result in results['matches']:
            metadata = json.loads(result['metadata']['response'])
            if isinstance(metadata, list):
                metadata = metadata[0]
            if metadata.get('title'):
                result['title'] = metadata['title']

        self.print_results(results, query, top_k)
        return results['matches']

    @staticmethod
    def print_results(results, query, top_k):
        print(f"Top {top_k} results for query: '{query}'")
        for match in results['matches']:
            print(f"ID: {match['id']}")
            print(f"Score: {match['score']}")
            print(f"Response: {match['metadata']['response'][:1000]}...")  # Print first 1000 characters of the response
            print("---")

if __name__ == "__main__":
    searcher = ArticleSearcher()
    search_query = "Find a Huntingtin protein interaction with ubiquitin and its role in protein degradation"
    logging.info(f"Search Query: {search_query}")
    searcher.search_for_articles(search_query)