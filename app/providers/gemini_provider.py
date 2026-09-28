from dotenv import load_dotenv
from google import genai
import os

from app.providers.base import ModelProvider


load_dotenv()


class GeminiProvider(ModelProvider):
    """
    Gemini implementation of the ModelProvider interface.
    """

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def generate(self, query: str, provider_model: str):

        interaction = self.client.interactions.create(
            model=provider_model,
            input=query
        )

        return interaction.output_text