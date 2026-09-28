from dotenv import load_dotenv
from google import genai
import os


# Load environment variables from .env
load_dotenv()


# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_response(model, query):
    """
    Generate a response using the selected AI model.
    Handles API errors gracefully.
    """

    try:

        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=query
        )

        return {
            "model": model["name"],
            "response": interaction.output_text,
            "status": "success"
        }

    except Exception as e:

        return {
            "model": model["name"],
            "response": "The selected AI provider is currently unavailable.",
            "status": "error",
            "error": str(e)
        }