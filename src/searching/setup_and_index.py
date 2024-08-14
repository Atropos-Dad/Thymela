import json
import os
import time
from typing import List, Dict
import logging
import joblib
import nltk
import tiktoken
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from tqdm import tqdm
import numpy as np
from dbwrap.db_get_result import get_all_results_original

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Constants
EMBEDDINGS_DIMENSIONS = 512
MAX_TOKENS = 8191
ENCODING_NAME = "cl100k_base"
PRICE_PER_TOKEN = 0.13 / 1000000
INDEX_NAME = "hybridhearchexperiment"
OPENAI_TOKEN_LIMIT = 1000000  # OpenAI token limit per minute
CHECKPOINT_FILE = 'embedding_checkpoint.json'

def check_config_files():
    """Check if necessary configuration files exist."""
    required_files = ['bm25_model.joblib', 'embedding_config.json', 'pinecone_config.json']
    missing_files = [file for file in required_files if not os.path.exists(file)]
    
    if missing_files:
        logger.info(f"Missing configuration files: {', '.join(missing_files)}")
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
    keys = ["studyId", "response", "source", "title", "projectDescription", "sampleProcessingProtocol", "dataProcessingProtocol","keywords", "organisms", "organismParts", "diseases", "projectTags", "instruments"]    
    return [dict(zip(keys, row)) for row in database_results]

async def fetch_database_results(limit: int = None):
    """Fetch results from the database asynchronously."""
    return await get_all_results_original(limit)

def load_checkpoint():
    """Load the checkpoint file if it exists."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {'processed_count': 0, 'result_list': []}

def save_checkpoint(processed_count: int, result_list: List[Dict]):
    """Save the current progress to a checkpoint file."""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'processed_count': processed_count, 'result_list': result_list}, f)

def get_embeddings(database_results: List[Dict], embedding_client: OpenAIEmbeddings) -> List[Dict]:
    """Generate embeddings for the database results."""
    checkpoint = load_checkpoint()
    result_list = checkpoint['result_list']
    processed_count = checkpoint['processed_count']
    
    batch_texts, batch_ids, batch_responses = [], [], []
    current_tokens, total_tokens, total_batches = 0, 0, 0
    start_time = time.time()
    token_count_last_minute = 0
    last_reset_time = time.time()

    with tqdm(total=len(database_results), initial=processed_count, desc="Generating embeddings") as pbar:
        for row in database_results[processed_count:]:
            text = ' '.join(f'{key}: {row[key]}' for key in row)
            tokens = num_tokens_from_string(text)

            if current_tokens + tokens > MAX_TOKENS or token_count_last_minute + tokens > OPENAI_TOKEN_LIMIT:
                if batch_texts:
                    embeddings = embedding_client.embed_documents(batch_texts)
                    result_list.extend([
                        {'studyId': id, 'response': response, 'embeddings': embedding}
                        for id, response, embedding in zip(batch_ids, batch_responses, embeddings)
                    ])
                    batch_texts, batch_ids, batch_responses = [], [], []
                    current_tokens = 0
                    total_batches += 1
                    processed_count += len(embeddings)
                    pbar.update(len(embeddings))
                    save_checkpoint(processed_count, result_list)

                # Check if we need to wait for rate limit
                current_time = time.time()
                if current_time - last_reset_time >= 60:
                    token_count_last_minute = 0
                    last_reset_time = current_time
                elif token_count_last_minute + tokens > OPENAI_TOKEN_LIMIT:
                    sleep_time = 60 - (current_time - last_reset_time)
                    logger.info(f"Rate limit approaching. Sleeping for {sleep_time:.2f} seconds.")
                    time.sleep(sleep_time)
                    token_count_last_minute = 0
                    last_reset_time = time.time()

            batch_texts.append(text)
            batch_ids.append(row['studyId'])
            batch_responses.append(str(row['response']))
            current_tokens += tokens
            total_tokens += tokens
            token_count_last_minute += tokens

    if batch_texts:
        embeddings = embedding_client.embed_documents(batch_texts)
        result_list.extend([
            {'studyId': id, 'response': response, 'embeddings': embedding}
            for id, response, embedding in zip(batch_ids, batch_responses, embeddings)
        ])
        total_batches += 1
        processed_count += len(embeddings)
        pbar.update(len(embeddings))
        save_checkpoint(processed_count, result_list)

    logger.info(f"Embedding generation completed in {time.time() - start_time:.2f} seconds.")
    logger.info(f"Total tokens: {total_tokens:,}, Total batches: {total_batches:,}")
    logger.info(f"Estimated cost: ${total_tokens * PRICE_PER_TOKEN:.6f}")

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

def limit_sparse_vector_size(sparse_vector, max_size=1000):
    if len(sparse_vector['indices']) > max_size:
        # Sort the sparse vector by values and keep the top 1000
        sorted_indices = np.argsort(sparse_vector['values'])[::-1][:max_size]
        return {
            'indices': [sparse_vector['indices'][i] for i in sorted_indices],
            'values': [sparse_vector['values'][i] for i in sorted_indices]
        }
    return sparse_vector

def truncate_metadata(metadata, max_bytes=40000):
    # Convert metadata to JSON string
    metadata_str = json.dumps(metadata)
    
    # If the metadata is already within the limit, return it as is
    if len(metadata_str.encode('utf-8')) <= max_bytes:
        return metadata
    
    # Truncate the 'text' field
    while len(json.dumps(metadata).encode('utf-8')) > max_bytes:
        metadata['text'] = metadata['text'][:-100]  # Remove last 100 characters
    
    return metadata

def group_embeddings_and_generate_sparse_vectors(cases: List[Dict], sparse_vector_model: BM25Encoder, database_results: List[Dict]):
    """Group embeddings and generate sparse vectors."""
    return [
        {
            'id': str(case['studyId']),
            'sparse_values': limit_sparse_vector_size(sparse_vector_model.encode_documents([' '.join(str(db_row[key]) for key in db_row)])[0]),
            'values': case['embeddings'],
            'metadata': truncate_metadata({
                'response': str(case['response']),
                'text': ' '.join(str(db_row[key]) for key in db_row)
            })
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
    if not files_exist and run_init_default:
        logger.info("Setting up index")
        logger.info("Setup NLTK")
        setup_nltk()

        logger.info("Fetching and processing database results")
        raw_results = await fetch_database_results(limit=10)
        database_results = process_database_results(raw_results)
        logger.debug(f"Retrieved {len(database_results)} records from the database.")

        logger.info("Generating embeddings")
        embedding_client = OpenAIEmbeddings(
            api_key=os.getenv('OPENAI_API_KEY'),
            model="text-embedding-3-large", 
            dimensions=EMBEDDINGS_DIMENSIONS
        )
        all_cases_with_embeddings = get_embeddings(database_results, embedding_client)


        logging.info("Setting up the BM25 model")
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

        logging.info("Uploading!")
        # Upsert vectors to Pinecone
        pinecone_index.upsert(vectors=all_cases_embeddings_and_sparse_vectors, batch_size=100)

        # Save configurations
        save_configurations(bm25_model, os.getenv('OPENAI_API_KEY'), os.getenv('PINECONE_API_KEY'))

        logging.debug("Setup and indexing complete. You can now use the search functionality.")

    elif not files_exist and not run_init_default:
        logger.error("No config files, and not running setup. Please run the setup process first.")