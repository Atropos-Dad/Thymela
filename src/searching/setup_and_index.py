import chromadb
from typing import List, Dict
import logging
from halo import Halo
from dotenv import load_dotenv

from dbwrap.db_get_result import get_all_results_original

# set up spinner
spinner = Halo(text='Adding to DB', spinner='dots')

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

collection_name = "hybridsearchexperiment"


def process_database_results(database_results: List[tuple]) -> List[Dict]:
    """Convert database results from tuples to dictionaries."""
    # pride keys
    keys = ["studyId", "response", "source", "title", "projectDescription", "sampleProcessingProtocol", "dataProcessingProtocol","keywords", "organisms", "organismParts", "diseases", "projectTags", "instruments"]
    
    # create a dictionary for each row
    processed_results = [dict(zip(keys, row)) for row in database_results]

    # for all keys that are not studyId, source, title, response, combine into one string with a key
    for result in processed_results:
        metadata = {}
        for key, value in result.items():
            if key not in ["studyId", "source", "title", "response"]:
                metadata[key] = value

        for key in metadata.keys():
            del result[key]


        result["text"] = str(metadata)

        

    return processed_results

async def fetch_database_results(limit: int = None):
    """Fetch results from the database asynchronously."""
    return await get_all_results_original(limit)


chroma_client = chromadb.PersistentClient(path="chromadb")

def add_document(database_result: Dict):
    collection=chroma_client.get_collection(name=collection_name)

    # convert dict to str
    database_result_str = str(database_result)
    

    # we're assuming stuff is coming in processed, singular
    collection.add(documents=[database_result_str], ids=[database_result['studyId']])


def add_documents(database_results: List[Dict]):
    collection=chroma_client.get_collection(name=collection_name)

    # convert dict to str
    database_results_str = [str(database_result) for database_result in database_results]
    
    collection.add(documents=database_results_str, ids=[database_result['studyId'] for database_result in database_results])

def check_for_db():
    # check if the collection is populated/exists
    try:
        chroma_client.get_collection(name=collection_name)
        return True
    except Exception as e:
        print(e)
        return False


async def init_and_index(run_init_default=False):
    collection_exists = check_for_db()
    if not collection_exists and run_init_default:
        logger.info("Setting up index")
        collection = chroma_client.create_collection(name=collection_name)

        logger.info("Fetching and processing database results")
        raw_results = await fetch_database_results(limit=None)
        database_results = process_database_results(raw_results)
        logger.debug(f"Retrieved {len(database_results)} records from the database.")

        spinner.start()
        add_documents(database_results)
        spinner.stop()

        logging.info(f"Number of records added: {collection.count()}")
        logging.debug("Setup and indexing complete. You can now use the search functionality.")

    elif not collection_exists and not run_init_default:
        logger.error("No config files, and not running setup. Please run the setup process first.")
