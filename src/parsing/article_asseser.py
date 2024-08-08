import os
import json
import logging
import re
from dotenv import load_dotenv
from prompting.prompt_manager import Prompt
from parsing.config import config
from parsing.API_Wrapper import LLM_Wrapper, LLM_Model
from parsing.content_getter import remove_newlines
from parsing.content_getter import make_json_safe
from dbwrap.db_get_study import get_n_studies

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the LLM Model 
LLM_Model = LLM_Wrapper(config["model"], 2)

# Set up logging configuration
import logging

def prompt_ai_with_article(study=None, file_path=None):
  
    if study is None and file_path is None:
        logger.error("No URL or file path provided!")
        return None

    # Read content from file if file_path is provided
    if file_path is not None:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        # Placeholder for fetching article content from URL (implement if needed)
        content = study

    if content is None:
        return None
    
    main_prompt_obj = Prompt(file_path="src/prompting/context_prompt.txt", variables={"content": content})

    # Get AI response using LLM_Model
    response = LLM_Model.prompt(main_prompt_obj)
    

    logger.debug(f"Raw Response from AI: {response}")
    #print(f"Raw Response from AI: {response}")
    
    if response is None:
        logger.warning(f"Empty response from AI!")

    return response

def assess_article(study, file_path_to_article=None):
    json_response = prompt_ai_with_article(study, file_path=file_path_to_article)
    if json_response is None:
        return None

    #logger.info(f"URL: {url}")
    #return json.dumps(json_response, indent=4)
    return json_response

def assess_multiple_studies(amount_of_studies):
    studies = get_n_studies(amount_of_studies)
    for study in studies:
        output = assess_article(study) 
        print(output)




