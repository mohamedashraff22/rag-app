from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging


class OpenAIProvider(LLMInterface):
    # I can use ollama with the same way but i will just add url to make requests go to it instead of the openai provider
    def __init__(
        self,
        api_key: str,
        api_url: str = None,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        # embeding_size : will be needed for the vector db
        self.embedding_model_id = None
        self.embedding_size = None

        args = {
            "api_key": self.api_key
        }

        # Only add base_url if it is not None AND not empty
        if self.api_url and str(self.api_url).strip():
            args["base_url"] = self.api_url

        self.client = OpenAI(**args)

        # __name__ -> name of the current file iam in.
        self.logger = logging.getLogger(__name__)

        # end of the init function

    # I did it outside the init, as this will allow me change configuration (during run time -> app in production),
    # if i do it as an object in it, once i define it at the start of the app.
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    # not in interface as may provider use it and another not, it for making the text as i want for all providers like lowercasing or whatever i want.
    # helper function for local usage in this class only (only all other function in this class only will use it).
    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: int = None,  # only in python interface we can set them to deafult value -> None , other languages may get errors
        temperature: float = None,
    ):

        # there is a problem in the client and it returns None
        if not self.client:
            # raise ValueError("OpenAI client was not set") # but i will not use this as this error will break my application.
            self.logger.error("OpenAI client was not set")
            # logger.info, logger.warning, logger.error
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None

        max_output_tokens = (
            max_output_tokens
            if max_output_tokens
            else self.default_generation_max_output_tokens
        )
        temperature = (
            temperature if temperature else self.default_generation_temperature
        )

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        # validations
        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
        ):
            self.logger.error("Error while generating text with OpenAI")
            return None

        return response.choices[0].message["content"]

    def embed_text(self, text: str, document_type: str = None):

        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text,
        )

        # validations
        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return response.data[0].embedding

    # OpenAI expect all messages to be like this, role and content should be in enum as they changing from provider to provider.
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}
