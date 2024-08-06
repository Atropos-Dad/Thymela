import json
import logging
from prompt_manager import Prompt
from parsing.API_Wrapper import LLM_Model

# Set up logger
logger = logging.getLogger(__name__)

def remove_newlines(text):
    """
    Removes newlines and escaped newlines from a text string.
    """
    try:
        return text.replace("\n", "").replace("\\\n", "")
    except Exception as e:
        logger.error(f"Error removing newlines: {e}")
        return text

def make_json_safe(text):
    """
    Escapes characters in a string to make it safe for JSON.
    """
    json_escaped = text.replace("\\", "\\\\")\
                     .replace('"', '\\"')\
                     .replace("\b", "\\b")\
                     .replace("\f", "\\f")\
                     .replace("\n", "\\n")\
                     .replace("\r", "\\r")\
                     .replace("\t", "\\t")

    non_ascii_escaped = []
    for char in json_escaped:
        if ord(char) >= 127:
            escaped_char = "\\u{:04x}".format(ord(char))
        else:
            escaped_char = char
        non_ascii_escaped.append(escaped_char)

    return ''.join(non_ascii_escaped)

def get_article_text_ai(content, url=None):
    """
    Processes the content of an article using an AI model.

    Parameters:
    content (str): The content of the article.
    url (str, optional): The URL of the article, for logging purposes.

    Returns:
    dict: A JSON response with features "is_article", "is_accessible", and "content".
          Returns None if the article is not accessible or not an article.
    """
    try:
        # Make the content JSON safe
        safe_content = make_json_safe(remove_newlines(content))

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Prompting AI with content: {safe_content[:500]}...")  # Log first 500 characters
        else:
            logger.info(f"Submitting content for analysis.")

        # Create a prompt with the content for the AI model
        prompt = Prompt(file_path="content_prompt", variables={"html": safe_content})
        
        # Get AI response using LLM_Model
        response = LLM_Model.prompt(prompt)

        response = remove_newlines(response)
        logger.debug(f"AI article output (content cleaning): {response[:500]}...")  # Log first 500 characters

        # Parse the AI response from JSON
        response_json = json.loads(response)

        # Add the original content to the response
        response_json["content"] = content

        # Check if the response indicates the article is a list
        if response_json['is_list'] in ["True", "true", True]:
            logger.warning(f"AI response indicates that the content is a list")
            return None
            
        # Check if the response indicates the article is accessible
        if response_json['is_accessible'] not in ["True", "true", True]:
            logger.warning(f"AI response indicates that the content is not accessible")
            return None
            
        # Check if the response indicates the content is an article
        if response_json['is_article'] not in ["True", "true", True]:
            logger.warning(f"AI response indicates that the content is not an article")
            return None

        # It's probably an article
        else:
            return response_json

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e.msg} at position {e.pos}")
        logger.error(f"Response causing error: {response}")
        return None
    except Exception as e:
        logger.error(f"Error processing content: {str(e)}")
        return None