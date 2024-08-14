import logging; logger = logging.getLogger(__name__)
import chromadb
import datetime
collection_name = "hybridsearchexperiment"
chroma_client = chromadb.PersistentClient(path="chromadb")
collection = chroma_client.get_collection(name=collection_name)    

def process_search_results(results):
    # for each result, we need to convert the result into this schema:
    # {
    #     "id": "unique_id",
    #     "score": 0.5,
    #    "metadata": {
    #        "response": "The response to the query",
    #        "text": "The source of the response"
    #    },
    #    title: "The title of the response",
    #    values: "The value of the response"
    #}

    # results has ids, and documents


    # print out the schema of the results
    # input(eval(results["documents"][0][1]).keys())
    processed_results = []
    
    for index, result in enumerate(results["documents"][0]):
        # convert from str to dict
        dict_result = eval(result)
        
        processed_result = {
            "id": results['ids'][0][index],
            "score": results['distances'][0][index],
            "response": dict_result['response'],
            "text": dict_result['text'],
            "title": dict_result['title'],
            "values": []
        }
        processed_results.append(processed_result)

    return processed_results

def search_for_articles(query: str, top_k: int = 5, alpha: float = 0.5):
    results = collection.query(
        query_texts=[query], # Chroma will embed this for you
        n_results=top_k # how many results to return
    )

    processed_results = process_search_results(results) 
    print_results(processed_results, query)
    return processed_results

def print_results(results, query):
    for match in results:
        logging.debug(f"Query: {query}")
        logging.debug(f"ID: {match['id']}")
        logging.debug(f"Score: {match['score']}")
        logging.debug(f"Response: {match['response'][:1000]}...")  # Print first 1000 characters of the response
        logging.debug(f"Response: {match['text'][:1000]}...")  # Print first 1000 characters of the response
        logging.debug("---")

# Example usage
# if __name__ == "__main__":
#     search_query = "Find a Huntingtin protein interaction with ubiquitin and its role in protein degradation"
#     logging.info(f"Search Query: {search_query}")
#     search_for_articles(search_query)
