"""
OpenAI provider module for handling text generation and embedding.
This module integrates with the OpenAI API (or compatible backends like Ollama).
"""

from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging
from typing import List, Union, Optional, Any


class OpenAIProvider(LLMInterface):
    """
    Provider implementation for OpenAI's LLM services.
    """

    def __init__(
        self,
        api_key: str,
        api_url: Optional[str] = None,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 1.0,
    ):
        """
        Initializes the OpenAI provider with API credentials and default settings.
        
        Args:
            api_key (str): OpenAI API key.
            api_url (Optional[str]): Custom base URL for API requests (e.g., for Ollama or proxies).
            default_input_max_characters (int): Maximum characters allowed for input processing.
            default_generation_max_output_tokens (int): Default token limit for generations.
            default_generation_temperature (float): Default temperature for generations.
        """
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url and self.api_url.strip() else None
        )

        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """
        Sets the model ID to be used for text generation.
        """
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Sets the model ID and dimension size for embeddings.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str) -> str:
        """
        Preprocesses input text, including truncation based on character limits.
        """
        return text[: self.default_input_max_characters].strip()

    def generate_text(
        self, 
        prompt: str, 
        chat_history: List[dict] = [], 
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Generates text using the configured OpenAI model.
        
        Args:
            prompt (str): The input prompt or query.
            chat_history (List[dict]): Previous conversation turns.
            max_output_tokens (Optional[int]): Token limit for this specific call.
            temperature (Optional[float]): Temperature for this specific call.
            
        Returns:
            Optional[str]: Generated text content or None on error.
        """
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model ID not set.")
            return None
        
        tokens = max_output_tokens or self.default_generation_max_output_tokens
        temp = temperature or self.default_generation_temperature

        # Append current prompt to history
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_completion_tokens=tokens,
                temperature=temp
            )

            if response and response.choices:
                return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Failed to generate text using OpenAI: {e}")

        return None

    def embed_text(self, text: Union[str, List[str]], document_type: str = None) -> Optional[List[List[float]]]:
        """
        Generates embeddings for the provided text(s).
        
        Args:
            text (Union[str, List[str]]): Singular text or list of texts to embed.
            document_type (str): Optional context for the embedding (not used by standard OpenAI).
            
        Returns:
            Optional[List[List[float]]]: List of embedding vectors or None on error.
        """
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        if isinstance(text, str):
            text = [text]

        if not self.embedding_model_id:
            self.logger.error("Embedding model ID not set.")
            return None
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id,
                input=text,
            )

            if response and response.data:
                return [rec.embedding for rec in response.data]
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings using OpenAI: {e}")

        return None

    def construct_prompt(self, prompt: str, role: str) -> dict:
        """
        Constructs a prompt dictionary in the format expected by OpenAI.
        """
        return {
            "role": role,
            "content": prompt
        }

