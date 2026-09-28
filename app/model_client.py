from app.providers.gemini_provider import GeminiProvider


# Create the Gemini provider
gemini_provider = GeminiProvider()


def generate_response(model, query):
    """
    Generate a response using the provider layer.

    The selected ModelMesh model contains information
    about which provider and provider model should be used.
    """

    try:

        response = gemini_provider.generate(
            query=query,
            provider_model=model["provider_model"]
        )

        return {
            "model": model["name"],
            "response": response,
            "status": "success"
        }

    except Exception as e:

        return {
            "model": model["name"],
            "response": "The selected AI provider is currently unavailable.",
            "status": "error",
            "error": str(e)
        }