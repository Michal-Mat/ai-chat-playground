import os
import logging
from typing import Optional, List, Dict, Union
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion
from openai.types import CreateEmbeddingResponse, Completion

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    A client wrapper for OpenAI API that handles authentication and common operations.
    """

    def __init__(
        self, api_key: Optional[str] = None, organization: Optional[str] = None
    ):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. If None, will try to load from OPENAI_API_KEY environment variable.
            organization: OpenAI organization ID. If None, will try to load from OPENAI_ORG_ID environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = organization or os.getenv("OPENAI_ORG_ID")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize OpenAI clients
        client_kwargs = {"api_key": self.api_key}
        if self.organization:
            client_kwargs["organization"] = self.organization

        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)

        logger.info("OpenAI client initialized successfully")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatCompletion:
        """
        Create a chat completion using OpenAI's chat models.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: The model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API call

        Returns:
            ChatCompletion response object
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            logger.info(f"Chat completion created with model: {model}")
            return response
        except Exception as e:
            logger.error(f"Error creating chat completion: {e}")
            raise

    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatCompletion:
        """
        Async version of chat completion.
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            logger.info(f"Async chat completion created with model: {model}")
            return response
        except Exception as e:
            logger.error(f"Error creating async chat completion: {e}")
            raise

    def completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo-instruct",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Completion:
        """
        Create a text completion using OpenAI's completion models.

        Args:
            prompt: The prompt to complete
            model: The model to use (default: gpt-3.5-turbo-instruct)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API call

        Returns:
            Completion response object
        """
        try:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            logger.info(f"Text completion created with model: {model}")
            return response
        except Exception as e:
            logger.error(f"Error creating completion: {e}")
            raise

    def create_embeddings(
        self,
        text: Union[str, List[str]],
        model: str = "text-embedding-3-small",
        **kwargs,
    ) -> CreateEmbeddingResponse:
        """
        Create embeddings for text using OpenAI's embedding models.

        Args:
            text: Text or list of texts to embed
            model: Embedding model to use (default: text-embedding-3-small)
            **kwargs: Additional parameters for the API call

        Returns:
            CreateEmbeddingResponse object
        """
        try:
            response = self.client.embeddings.create(model=model, input=text, **kwargs)
            logger.info(f"Embeddings created with model: {model}")
            return response
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise

    def list_models(self) -> List[str]:
        """
        List available OpenAI models.

        Returns:
            List of model names
        """
        try:
            models = self.client.models.list()
            model_names = [model.id for model in models.data]
            logger.info(f"Retrieved {len(model_names)} available models")
            return model_names
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise

    def simple_chat(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Simple chat interface for quick interactions.

        Args:
            message: The message to send
            model: The model to use

        Returns:
            The response text
        """
        messages = [{"role": "user", "content": message}]
        response = self.chat_completion(messages, model=model)
        return response.choices[0].message.content

    def simple_complete(
        self, prompt: str, model: str = "gpt-3.5-turbo-instruct"
    ) -> str:
        """
        Simple completion interface for quick text completion.

        Args:
            prompt: The prompt to complete
            model: The model to use

        Returns:
            The completion text
        """
        response = self.completion(prompt, model=model)
        return response.choices[0].text

    def get_embedding_vector(
        self, text: str, model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Get embedding vector for a single text.

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            List of float values representing the embedding
        """
        response = self.create_embeddings(text, model=model)
        return response.data[0].embedding


# Convenience function to create a client instance
def create_openai_client(
    api_key: Optional[str] = None, organization: Optional[str] = None
) -> OpenAIClient:
    """
    Create an OpenAI client instance.

    Args:
        api_key: OpenAI API key. If None, will try to load from environment.
        organization: OpenAI organization ID. If None, will try to load from environment.

    Returns:
        OpenAIClient instance
    """
    return OpenAIClient(api_key=api_key, organization=organization)
