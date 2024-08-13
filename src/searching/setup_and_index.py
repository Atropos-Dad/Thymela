import json
import os
import time
from typing import List, Dict
import logging; logger = logging.getLogger(__name__)
import joblib
import nltk
import tiktoken
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from tqdm import tqdm

from dbwrap.db_get_result import get_all_results_original

# Load environment variables
load_dotenv()

# Constants
EMBEDDINGS_DIMENSIONS = 512
MAX_TOKENS = 8191
ENCODING_NAME = "cl100k_base"
PRICE_PER_TOKEN = 0.13 / 1000000
INDEX_NAME = "hybridhearchexperiment"

def check_config_files():
    """Check if necessary configuration files exist."""
    required_files = ['bm25_model.joblib', 'embedding_config.json', 'pinecone_config.json']
    missing_files = [file for file in required_files if not os.path.exists(file)]
    
    if missing_files:
        logging.info(f"Missing configuration files: {', '.join(missing_files)}")
        return False
    return True

def setup_nltk():
    """Download NLTK data if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

def num_tokens_from_string(string: str, encoding_name: str = ENCODING_NAME) -> int:
    """Calculate the number of tokens in a string."""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

def process_database_results(database_results: List[tuple]) -> List[Dict]:
    """Convert database results from tuples to dictionaries."""
    keys = ['studyId', 'response', 'source', 'title', 'projectDescription', 'sampleProcessingProtocol',
            'dataProcessingProtocol', 'keywords', 'organisms', 'organismParts', 'diseases', 'projectTags', 'instruments']
    return [dict(zip(keys, row)) for row in database_results]

async def fetch_database_results(limit: int = None):
    """Fetch results from the database asynchronously."""
    return await get_all_results_original(limit)

def get_embeddings(database_results: List[Dict], embedding_client: OpenAIEmbeddings) -> List[Dict]:
    """Generate embeddings for the database results."""
    result_list = []
    batch_texts, batch_ids, batch_responses = [], [], []
    current_tokens, total_tokens, total_batches = 0, 0, 0
    start_time = time.time()

    for row in database_results:
        text = ' '.join(str(row[key]) for key in row)
        tokens = num_tokens_from_string(text)

        if current_tokens + tokens > MAX_TOKENS:
            if batch_texts:
                embeddings = embedding_client.embed_documents(batch_texts)
                result_list.extend([
                    {'studyId': id, 'response': response, 'embeddings': embedding}
                    for id, response, embedding in zip(batch_ids, batch_responses, embeddings)
                ])
                batch_texts, batch_ids, batch_responses = [], [], []
                current_tokens = 0
                total_batches += 1

        batch_texts.append(text)
        batch_ids.append(row['studyId'])
        batch_responses.append(str(row['response']))
        current_tokens += tokens
        total_tokens += tokens

    if batch_texts:
        embeddings = embedding_client.embed_documents(batch_texts)
        result_list.extend([
            {'studyId': id, 'response': response, 'embeddings': embedding}
            for id, response, embedding in zip(batch_ids, batch_responses, embeddings)
        ])
        total_batches += 1

    logging.info(f"Embedding generation completed in {time.time() - start_time:.2f} seconds.")
    logging.debug(f"Total tokens: {total_tokens:,}, Total batches: {total_batches:,}")
    logging.debug(f"Estimated cost: ${total_tokens * PRICE_PER_TOKEN:.6f}")

    return result_list

def setup_pinecone(api_key: str):
    """Set up Pinecone index."""
    pc = Pinecone(api_key=api_key)
    
    if INDEX_NAME in pc.list_indexes().names():
        pc.delete_index(INDEX_NAME)
        logging.debug(f"Deleted old index: {INDEX_NAME}")

    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDINGS_DIMENSIONS,
        metric="dotproduct",
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

    while not pc.describe_index(INDEX_NAME).status['ready']:
        time.sleep(1)

    return pc.Index(INDEX_NAME)

def train_bm25(database_results: List[Dict]):
    """Train BM25 model on the database results."""
    train_texts = [' '.join(str(row[key]) for key in row) for row in database_results]
    bm25 = BM25Encoder()
    bm25.fit(train_texts)
    return bm25

def group_embeddings_and_generate_sparse_vectors(cases: List[Dict], sparse_vector_model: BM25Encoder, database_results: List[Dict]):
    """Group embeddings and generate sparse vectors."""
    return [
        {
            'id': str(case['studyId']),
            'sparse_values': sparse_vector_model.encode_documents([' '.join(str(db_row[key]) for key in db_row)])[0],
            'values': case['embeddings'],
            'metadata': {
                'response': str(case['response']),
                'text': ' '.join(str(db_row[key]) for key in db_row)
            }
        }
        for case, db_row in tqdm(zip(cases, database_results), desc="Processing cases", total=len(cases))
    ]

def save_configurations(bm25_model: BM25Encoder, openai_api_key: str, pinecone_api_key: str):
    """Save configurations to files."""
    joblib.dump(bm25_model, 'bm25_model.joblib')
    
    with open('embedding_config.json', 'w') as f:
        json.dump({
            'api_key': openai_api_key,
            'model': "text-embedding-3-large",
            'dimensions': EMBEDDINGS_DIMENSIONS
        }, f)

    with open('pinecone_config.json', 'w') as f:
        json.dump({
            'api_key': pinecone_api_key,
            'index_name': INDEX_NAME
        }, f)

async def init_and_index(run_init_default=False):
    files_exist = check_config_files()
    if not files_exist and run_init_default: # if files are not found, and asked to run
        logging.info("Setting up index")
        logging.info("Setup NLTK")
        setup_nltk()

        logging.info("Fetching and processing database results")
        # Fetch and process database results
        raw_results = await fetch_database_results(limit=None)  # Set limit to None for all results
        database_results = process_database_results(raw_results)
        logging.debug(f"Retrieved {len(database_results)} records from the database.")

        logging.info("Generating embeddings")
        # Generate embeddings
        embedding_client = OpenAIEmbeddings(
            api_key=os.getenv('OPENAI_API_KEY'),
            model="text-embedding-3-large", 
            dimensions=EMBEDDINGS_DIMENSIONS
        )
        all_cases_with_embeddings = get_embeddings(database_results, embedding_client)


        # Set up Pinecone
        pinecone_index = setup_pinecone(os.getenv('PINECONE_API_KEY'))

        logging.info("Train the BM25 model")
        # Train BM25 model
        bm25_model = train_bm25(database_results)

        logging.info("Generating vectors")
        # Group embeddings and generate sparse vectors
        all_cases_embeddings_and_sparse_vectors = group_embeddings_and_generate_sparse_vectors(
            all_cases_with_embeddings, bm25_model, database_results
        )

        logging.info("Upserting to pinecone!")
        # Upsert vectors to Pinecone
        pinecone_index.upsert(vectors=all_cases_embeddings_and_sparse_vectors, batch_size=100)

        # Save configurations
        save_configurations(bm25_model, os.getenv('OPENAI_API_KEY'), os.getenv('PINECONE_API_KEY'))

        logging.info("Setup and indexing complete. You can now use the search functionality.")

    elif not files_exist and not run_init_default:
        logging.error("No config files, and not running setup. Please run the setup process first.")
