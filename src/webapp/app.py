from flask import Flask, request, render_template, jsonify
import joblib
import json
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
from dotenv import load_dotenv
import os

app = Flask(__name__)

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

def search_articles(query: str, top_k: int = 5, alpha: float = 0.5):
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
    return results['matches']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_articles(query)
        return render_template('results.html', results=results, query=query)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)