import re

class Prompt:
    def __init__(
        self, system_prompt="", user_input="", variables={}, examples=[], file_path=None
    ):
        # If a file path is provided, create a prompt from the file
        if file_path:
            system_prompt, user_input, examples = self.create_prompt_from_file(
                file_path
            )

        # Ensure at least one of the parameters is provided
        if not system_prompt and not user_input and not examples:
            raise ValueError("All three parameters cannot be empty.")

        # Initialize the class attributes
        self.system_prompt = system_prompt
        self.examples = examples
        self.variables = variables
        self.user_input = user_input

    @classmethod
    def create_prompt_from_file(cls, file_path):
        """
        Load a prompt from a txt file. The file should be formatted as follows:

        ""
        <system_prompt>
            ...
        </system_prompt>
        <examples>
            ...
        </examples>
        <user_input>
            ...
        </user_input>
        ""

        If system_prompt or user_input is not found, the prompt will not be created, however examples are optional.
        Examples must be in this user, ai_response format:
        <user> example user content </user>
        <ai_response> example ai response </ai_response>
        """
        
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Extract system_prompt, user_input, and examples content from the file
        system_prompt = cls.extract_content(content, "system_prompt")
        user_input = cls.extract_content(content, "user_input")
        examples_content = cls.extract_content(content, "examples")

        # Ensure system_prompt and user_input are present
        if not system_prompt.strip() or not user_input.strip():
            raise ValueError("Missing system prompt or user input in file")

        # Parse examples content if present
        examples = cls.parse_examples(examples_content)

        return (system_prompt, user_input, examples)

    @staticmethod
    def extract_content(content, tag):
        # Extract content between specified tags
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def parse_examples(examples_content):
        # Define patterns to extract user and ai_response examples
        user_pattern = r"<user>(.*?)</user>"
        ai_pattern = r"<ai_response>(.*?)</ai_response>"

        # Find all user and ai_response examples
        users = re.findall(user_pattern, examples_content, re.DOTALL)
        ai_responses = re.findall(ai_pattern, examples_content, re.DOTALL)

        # Combine users and ai_responses into a list of tuples
        return list(zip(users, ai_responses))

    def set_system_prompt(self, prompt):
        # Set the system prompt
        self.system_prompt = prompt

    def add_example(self, user, ai_response):
        # Add an example to the list
        self.examples.append((user, ai_response))

    def set_variables(self, variables):
        # Set multiple variables at once
        self.variables = variables

    def add_variable(self, name, value):
        # Add a single variable to the dictionary
        self.variables[name] = value

    def get_user_input(self):
        # Format the user input with the variables
        return self.user_input.format(**self.variables)

    def export_to_txt(self, file_path):
        # Export the prompt to a text file
        with open(file_path, "w") as file:
            file.write("<system_prompt>\n")
            file.write(self.system_prompt + "\n")
            file.write("</system_prompt>\n")
            if self.examples:
                file.write("<examples>\n")
                for user, ai_response in self.examples:
                    file.write(f"<user>{user}</user>\n")
                    file.write(f"<ai_response>{ai_response}</ai_response>\n")
                file.write("</examples>\n")
            file.write("<user_input>\n")
            file.write(self.user_input)
            file.write("</user_input>")

    def __str__(self) -> str:
        # String representation of the object
        output = self.system_prompt + "\n"
        for user, ai_response in self.examples:
            output += f"User: {user}\nAI: {ai_response}\n"
        return output

    def __repr__(self) -> str:
        # Representation of the object for debugging
        return self.__str__()