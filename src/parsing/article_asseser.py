
from datetime import datetime
import json
from prompt_manager import Prompt
from test_saving import append_to_csv, process_entry
import feedparser

# Set up logging configuration
import logging

logger = logging.getLogger(__name__)

from API_Wrapper import LLM_Model

def prompt_ai_with_article(url = None, file_path = None):
    
    """
    This function prompts the AI with an article and returns the AI's response.

    Parameters:
    url (str): The URL of the article to be processed or
    file_path (str): The file path of the article to be processed.

    Returns:
    response: The AI's response to the article content.
    """
    if url is None and file_path is None:
        logger.error("No URL or file path provided!")
        return None

    # Read content from file if file_path is provided
    if file_path is not None:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        # Get article content from URL
        content = get_article_text_ai(url)

    if content == None:
        logger.error(
            f"The article at URL - {url} - content was not able to be analyzed by AI Model 2, This is probably as the content was REFUSED by AI Model 1 or UNACESSIBLE."
        )
        return None

    logger.info(f"Prompting AI 1 with article with url {url}")
        
    # Create a Prompt object with the article content
    main_prompt_obj = Prompt(file_path="context_prompt", variables={"content": content})

    # Get AI response using LLM_Model
    response = LLM_Model.prompt(main_prompt_obj)

    logger.debug(f"Raw Response from AI: {response}")

    if response == None:
        logger.warning(f"Empty response! {response.candidates[0].safety_ratings}")

    return response


def assess_article(url, file_path_to_article=None, save_to_file=False):
    """
    This function assesses an article by prompting the AI with the article's content,
    processes the AI's response, and optionally saves the result to a file.

    Parameters:
    url (str): The URL of the article to be assessed.
    file_path_to_article (str): The file path of the article to be assessed.
    save_to_file (bool): Flag to determine whether to save the response to a file.

    Returns:
    dict or list: The processed response from the AI.
    """
    logger.debug(f"{url}")
    response = prompt_ai_with_article(url, file_path=file_path_to_article)

    if response is None:
        return None
    
    # Get the current date in the format "DD-MM-YYYY"
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Clean up the response format if it's a JSON string wrapped in code block markers
    response = response.rstrip()
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]

    try:
        json_read = json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        logger.error(f"Response causing error: {response}")
        return None
    
    # Check if the decoded JSON is a list
    if isinstance(json_read, list):
        for entry in json_read:
            if save_to_file:
                process_entry(entry, url)
            append_to_csv(url, entry)
    else:
        if save_to_file: process_entry(json_read, url)
        append_to_csv(url, json_read)

    logger.info(f"URL: {url}")
    logger.info(f"Date: {current_date}")
    return json_read


def fetch_feed_links(url):
    """
    Fetches the links of articles from an RSS feed.

    Parameters:
    url (str): The URL of the RSS feed.

    Returns:
    list: A list of article links from the RSS feed.
    """
    feed = feedparser.parse(url)
    links = []
    for entry in feed.entries:
        links.append(entry.link)
    return links


def assess_article_rss_feed(rss_feed_url):
    """
    Assesses all articles linked in an RSS feed.

    Parameters:
    rss_feed_url (str): The URL of the RSS feed.

    Returns:
    list: Each processed response from the AI for each article in the RSS feed.
    """
    
    links = fetch_feed_links(rss_feed_url)
    for link in links:
        return assess_article(link)