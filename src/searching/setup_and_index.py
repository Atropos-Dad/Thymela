import pandas as pd
from tabulate import tabulate
import time
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
import tiktoken
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from tqdm import tqdm
import joblib
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read the CSV file
df = pd.read_csv(r"C:\Users\dylan\Downloads\10_Examples.csv")

row_count = df.shape[0]
print(f"The DataFrame contains {row_count} rows.")

EMBEDDINGS_DIMENSIONS = 512

embedding_client = OpenAIEmbeddings(
    api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-3-large", 
    dimensions=EMBEDDINGS_DIMENSIONS
)

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_embeddings(
    df: pd.DataFrame,
    num_rows: int = 2,
    max_tokens: int = 8191,
    encoding_name: str = "cl100k_base",
    price_per_token: float = 0.13 / 1000000
) -> List[Dict]:
    result_list = []
    batch_texts = []
    batch_ids = []
    current_tokens = 0
    total_tokens = 0
    total_batches = 0

    start_time = time.time()

    for index, row in df.head(num_rows).iterrows():
        text = f"{row['studyId']} {row['response']} {row['created']} {row['source']} {row['version']}"
        text = ' '.join(str(item) for item in text.split())  # Convert all items to strings

        if not isinstance(text, str) or not text.strip():
            continue

        tokens = num_tokens_from_string(text, encoding_name)

        if current_tokens + tokens > max_tokens:
            if batch_texts:
                embeddings = embedding_client.embed_documents(batch_texts)
                for i, text in enumerate(batch_texts):
                    result_list.append({
                        'studyId': batch_ids[i],
                        'response': str(df.loc[df['studyId'] == batch_ids[i], 'response'].values[0]),
                        'embeddings': embeddings[i]
                    })

            batch_texts = [text]
            batch_ids = [row['studyId']]
            current_tokens = tokens
            total_batches += 1
        else:
            batch_texts.append(text)
            batch_ids.append(row['studyId'])
            current_tokens += tokens

        total_tokens += tokens

    if batch_texts:
        embeddings = embedding_client.embed_documents(batch_texts)
        for i, text in enumerate(batch_texts):
            result_list.append({
                'studyId': batch_ids[i],
                'response': str(df.loc[df['studyId'] == batch_ids[i], 'response'].values[0]),
                'embeddings': embeddings[i]
            })
        total_batches += 1

    end_time = time.time()
    duration = end_time - start_time

    print(f"Completed in {duration:.2f} seconds.")
    print(f"Total number of tokens: {total_tokens:,}")
    print(f"Total number of batches: {total_batches:,}")
    print(f"Money burned: ${total_tokens * price_per_token:.6f}")

    return result_list

all_cases_with_embeddings = get_embeddings(df, num_rows=row_count)

# Pinecone setup
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

index_name = "hybridhearchexperiment"

existing_indexes = pc.list_indexes().names()

if index_name in existing_indexes:
    pc.delete_index(index_name)
    print("Deleted old index.")

pc.create_index(
    name=index_name,
    dimension=EMBEDDINGS_DIMENSIONS,
    metric="dotproduct",
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
)

while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

pinecone_index = pc.Index(index_name)
pinecone_index.describe_index_stats()

bm25 = BM25Encoder()

# Train BM25 on the combined text fields
train_texts = df['studyId'].astype(str) + ' ' + df['response'].astype(str) + ' ' + df['created'].astype(str) + ' ' + df['source'].astype(str) + ' ' + df['version'].astype(str)
bm25.fit(train_texts.tolist())

def group_embeddings_and_generate_sparse_vectors(cases, sparse_vector_model):
    all_cases_embeddings_and_sparse_vectors = []

    for case in tqdm(cases, desc="Processing cases"):
        studyId = case['studyId']
        response = case['response']
        text = f"{studyId} {response} {df.loc[df['studyId'] == studyId, 'created'].values[0]} {df.loc[df['studyId'] == studyId, 'source'].values[0]} {df.loc[df['studyId'] == studyId, 'version'].values[0]}"
        text = ' '.join(str(item) for item in text.split())  # Convert all items to strings
        embeddings = case['embeddings']

        sparse_values = sparse_vector_model.encode_documents([text])

        new_case_dict = {
            'id': str(studyId),
            'sparse_values': sparse_values[0],
            'values': embeddings,
            'metadata': {
                'response': str(response),
                'text': text
            }
        }

        all_cases_embeddings_and_sparse_vectors.append(new_case_dict)

    return all_cases_embeddings_and_sparse_vectors

all_cases_embeddings_and_sparse_vectors = group_embeddings_and_generate_sparse_vectors(all_cases_with_embeddings, bm25)

pinecone_index.upsert(vectors=all_cases_embeddings_and_sparse_vectors, batch_size=100)

# Save the BM25 model
joblib.dump(bm25, 'bm25_model.joblib')

# Save the embedding model configuration
with open('embedding_config.json', 'w') as f:
    json.dump({
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': "text-embedding-3-large",
        'dimensions': EMBEDDINGS_DIMENSIONS
    }, f)

# Save the Pinecone configuration
with open('pinecone_config.json', 'w') as f:
    json.dump({
        'api_key': os.getenv('PINECONE_API_KEY'),
        'index_name': index_name
    }, f)

print("Setup and indexing complete. You can now use the search functionality.")