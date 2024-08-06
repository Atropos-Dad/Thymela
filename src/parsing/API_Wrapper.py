import importlib
from prompt_manager import Prompt 
import logging
from dotenv import load_dotenv
import os
from config import config
logger = logging.getLogger(__name__)


class API_Wrapper:
    """
    Wrapper class for interacting with various AI APIs.
    """

    def __init__(self, library_name: str = None):
        load_dotenv()
        self.lib = importlib.import_module(library_name) # difference between this and normal import is 9.279994264943529e-08 seconds. So it's not a big deal. if we're only doing it once.

    def _prompt_api(self, prompt_str: str, variables: dict):
        pass

    def _parse_api_response(self, response):
        pass

    def _format_prompt_obj(self, prompt_obj: Prompt):
        # Convert the prompt object into an accepted format for the concrete api_wrapper object
        pass

    def prompt_content(self, prompt: Prompt):
        pass


class OpenAI_API(API_Wrapper):
    """
    Class for interacting with the OpenAI API.
    """

    def __init__(self, model_type=None):
        library_name = 'openai'
        # gpt-4o-mini should be used in place of gpt-3.5-turbo, as it is cheaper, more capable, multimodal, and just as fast. -openAI docs
        # Even 4o-mini outperforms even 4-turbo in some cases. - reddit post
        # Unsure which of these will perform best. But they are all here to be tried.
        model_type_dict = {
            "2": "gpt-4o",
            "1": "gpt-40 mini",
            "0": "gpt-4-turbo",
        }

        if model_type in model_type_dict:
            self.model_type = model_type_dict[model_type]
        else:
            self.model_type = 'gpt-4o'

        super().__init__(library_name)
        self.client  = self.lib.OpenAI()  # No need to os.getenv() the api key here, as the openai library does it for us.

    def _prompt_api(self, formated_prompt_messages):
        """
        Sends the prompt to the OpenAI API and returns the response.

        Parameters:
        formated_prompt_messages (list): List of formatted prompts in context_prompt - system prompt, user prompt, examples etc.

        Returns:
        response: The response from the API.
        """
        response = self.client.chat.completions.create(
            model=self.model_type, messages=formated_prompt_messages
        )
        return response

    def _parse_api_response(self, response):
        """
        Parses the response from the API.
        """
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("API response content is blank")
        return content

    def _format_prompt_obj(self, prompt_obj: Prompt):
        """
        Formats the prompt object for the API.

        Parameters:
        prompt_obj (Prompt): The prompt object containing the user input and examples.
        """
        
        messages = []

        if prompt_obj.system_prompt is not None:
            messages.append({"role": "system", "content": prompt_obj.system_prompt})

        for user, ai_response in prompt_obj.examples:
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": ai_response})

        # format the user input to use the variables
        messages.append({"role": "user", "content": prompt_obj.get_user_input()})

        return messages

    def prompt_content(self, prompt: Prompt):
        """
        Prompts the OpenAI API with the prompt and returns the AI response.

        Parameters:
        prompt (Prompt): The prompt object ie Sytem prompt containing the user input and examples.

        Returns:
        str: The content from the AI's response.
        """
        formated_prompt_messages = self._format_prompt_obj(prompt)
        # prompt the api 
        response = self._prompt_api(formated_prompt_messages)
        # get the results we actually need
        content = self._parse_api_response(response)
        return content


class Gemini_API_wrapper(API_Wrapper):
    """
    Class for interacting with the Gemini API.
    """

    model_config = {
        "temperature": 1
    }
    safety_config = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
    
    api_key_name = "GOOGLE_API_KEY"

    def __init__(self, defined_model_config=None, defined_safety_config=None, model_type=None):
        library_name = 'google.generativeai'
        
        if defined_model_config is not None:
            self.model_config = defined_model_config

        if defined_safety_config is not None:
            self.safety_config = defined_safety_config

        model_type_dict = {
            0: "gemini-1.0-pro",
            1: "gemini-1.5-flash",
            2: "gemini-1.5-pro",
        }

        if model_type in model_type_dict:
            self.model_type = model_type_dict[model_type]
        else:
            self.model_type = "gemini-1.5-pro"

        os.environ["GRPC_VERBOSITY"] = "ERROR"
        os.environ["GLOG_minloglevel"] = "2"

        super().__init__(library_name)

        # Configure the Gemini API
        self.lib.configure(api_key=os.getenv(self.api_key_name))

    def update_temperature(self, temperature):
        """
        Updates the temperature setting for the model.

        Parameters:
        temperature (float): The new temperature value, bounded between 0 and 2.
        """
        
        if temperature < 0:
            temperature = 0
        elif temperature > 2:
            temperature = 2

        self.model_config["temperature"] = temperature

    def _prompt_api(self, prompt):
        """
        Sends the prompt to the Gemini API and returns the response.

        Parameters:
        prompt (str): The formatted prompt string.

        Returns:
        response: The response from the API.
        """

        #================================================
        # in theory we can do stuff like this - but it's not implemented in the library yet, so we'll just use the basic prompt function:
        # model = self.lib.GenerativeModel(self.model_type, generation_config=self.model_config, safety_settings=self.safety_config, system_instruction=prompt.system_prompt)
        # response = model.generate_content(prompt.meesages)
        # return response
        #================================================

        model = self.lib.GenerativeModel(self.model_type, generation_config=self.model_config, safety_settings=self.safety_config)
        response = model.generate_content(prompt)
        return response

    def _parse_api_response(self, response):
        """
        Parses the response from the Gemini API.

        Parameters:
        response: The response from the API.

        Returns:
        str: The content of the response.
        """
        try:
            if response.text is not None:
                return response.text
        except ValueError:
            logger.error("Response text is not available, full response: ", response)

    def _format_prompt_obj(self, prompt_obj: Prompt):
    
        #Formats the prompt object for the Gemini API.
    	
        prompt_output_str = ""
        prompt_output_str += (
            prompt_obj.system_prompt + "\n\n"
        )  # gemini beta allows for proper sys prompt in. For now... TODO

        prompt_output_str += prompt_obj.system_prompt + "\n\n"
        
        if prompt_obj.examples:
            prompt_output_str += "The following are examples of the desired output:\n"

            for i, (user, ai_response) in enumerate(prompt_obj.examples):
                prompt_output_str += f"Example {i+1}:\nExample User Prompt: {user}\nExample AI Response: {ai_response}\n\n"

        if prompt_obj.user_input:
            prompt_output_str += f"Real User Prompt: {prompt_obj.get_user_input()}\n"

        return prompt_output_str

    def prompt_content(self, prompt: Prompt):
        """
        This public function combines both the private functions to prompt the AI and parse its response.
        """
        
        formatted_prompt = self._format_prompt_obj(prompt)
        response = self._prompt_api(formatted_prompt)

        content = self._parse_api_response(response)

        return content


class Claude_API_Wrapper(API_Wrapper):
    """
    Class for interacting with the Claude API.
    """

    api_key_name = "CLAUDE_API_KEY"

    def __init__(self, model_type=None):
        library_name = "anthropic"

        model_type_dict = {
            0: 'claude-3-haiku-20240307',
            1: 'claude-3-opus-20240229',
            2: 'claude-3-sonnet-20240229',
        } #claude for some reeason only works temp=1

        if model_type in model_type_dict:
            self.model_type = model_type_dict[model_type]
        else:
            self.model_type = 'claude-3-sonnet-20240229'
        super().__init__(library_name)
        self.client = self.lib.Anthropic(api_key=os.getenv(self.api_key_name))
        
    def _prompt_api(self, formatted_prompt_dict):
        """
        Sends the prompt to the API and returns the response.

        Parameters:
        formatted_prompt_dict (dict): Dictionary containing the formatted prompt.

        Returns:
        response: The response from the API.
        """
        messages = formatted_prompt_dict.get("messages", None)
        system_prompt = formatted_prompt_dict.get("system_prompt", None)

        if not messages:
            raise ValueError(
                "Prompt object does not have any messages to prompt the API with."
            )

        response = self.client.messages.create(
            model=self.model_type,
            messages=messages,
            system=system_prompt,
            max_tokens=1000,
        )

        return response

    def _parse_api_response(self, response):
        """
        Parses the response from the API.
        """
        content = response.content[0].text
        if not content:
            raise Exception("API response content is blank")
        return content

    def _format_prompt_obj(self, prompt_obj: Prompt):
        """
        Formats the prompt object for the API.
        
        Returns:
        dict: Dictionary containing formatted messages for the API.
        """
        formatted_prompt_dict = {}
        
        messages = []

        for user, ai_response in prompt_obj.examples:
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": ai_response})

        messages.append({"role": "user", "content": prompt_obj.get_user_input()})

        formatted_prompt_dict["messages"] = messages

        # System prompt here
        if prompt_obj.system_prompt:
            formatted_prompt_dict["system_prompt"] = prompt_obj.system_prompt

        return formatted_prompt_dict

    def prompt_content(self, prompt: Prompt):

        formatted_prompt = self._format_prompt_obj(prompt)
        response = self._prompt_api(formatted_prompt)
        content = self._parse_api_response(response)
        return content


class LLM_Wrapper:
    """
    A user should be able to initialize this class API with a key, and then prompt the API with a prompt and variables.
    They should also be able to give a 0-3 scale of LLM model to pick from (3 being more expensive and more accurate).
    The user should not have to worry about the specifics of which LLM model is being used, just the prompting and parsing.
    """

    def __init__(self, api_type: str, model_tier: int):
        self.api_type = api_type.lower()
        self.model_tier = model_tier
        self.api_wrapper = self._create_api_wrapper()

    def _create_api_wrapper(self):
        """
        Creates the appropriate API wrapper instance based on the api_type.

        Returns:
        API_Wrapper: The specific API wrapper instance.
        """
        if self.api_type == 'openai':
            return OpenAI_API(model_type=self.model_tier)
        elif self.api_type == "gemini":
            return Gemini_API_wrapper(model_type=self.model_tier)
        elif self.api_type == "claude":
            return Claude_API_Wrapper(model_type=self.model_tier)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")

    def prompt(self, prompt_obj: Prompt):
        """
        Prompts the API with the given prompt object and returns the response content.

        Parameters:
        prompt_obj (Prompt): The prompt object containing the user input and examples.

        Returns:
        str: The content from the API response.
        """
        return self.api_wrapper.prompt_content(prompt_obj)



# Check if only one api key is provided in .env, if so, create that API wrapper
# otherwise use gemini

LLM_Model = None


# test if config["model"] is not an empty string
if config["model"]:
    LLM_Model = LLM_Wrapper(config["model"], 2)

else:
    # Define the possible API keys
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GOOGLE_API_KEY')
    }

    # Filter out None values
    valid_keys = {key: value for key, value in api_keys.items() if value}

    # Check the number of valid API keys
    if len(valid_keys) == 1:
        api_key_name = list(valid_keys.keys())[0]
        if api_key_name == 'OPENAI_API_KEY':
            config["model"] = "openai"
        elif api_key_name == 'CLAUDE_API_KEY':
            config["model"] = "claude"
        else:
            config["model"] = "gemini"



    elif not config["model"]:
        Exception("No model provided in config or arguments!")

# GLOBAL LLM MODEL
LLM_Model = LLM_Wrapper(config["model"], 2)