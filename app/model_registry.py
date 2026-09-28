MODELS = [

    {
        "name": "Model-A",
        "quality": 0.91,
        "latency": 100,
        "cost": 0.02,
        "role": "cheap",
        "provider": "gemini",
        "provider_model": "gemini-3.8-flash"
    },

    {
        "name": "Model-B",
        "quality": 0.94,
        "latency": 250,
        "cost": 0.08,
        "role": "balanced",
        "provider": "gemini",
        "provider_model": "gemini-3.8-flash"
    },

    {
        "name": "Model-C",
        "quality": 0.97,
        "latency": 600,
        "cost": 0.40,
        "role": "powerful",
        "provider": "gemini",
        "provider_model": "gemini-3.8-flash"
    }

]


def get_models():
    return MODELS