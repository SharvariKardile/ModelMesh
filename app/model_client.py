from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_response(model, query):
    """
    Generate a response using the selected AI model.
    """

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=query
    )

    return {
        "model": model["name"],
        "response": interaction.output_text
    }