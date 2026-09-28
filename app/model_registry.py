MODELS = [

    {
        "name": "Model-A",
        "quality": 0.91,
        "latency": 100,
        "cost": 0.02,
        "role": "cheap"
    },

    {
        "name": "Model-B",
        "quality": 0.94,
        "latency": 250,
        "cost": 0.08,
        "role": "balanced"
    },

    {
        "name": "Model-C",
        "quality": 0.97,
        "latency": 600,
        "cost": 0.40,
        "role": "powerful"
    }

]


def get_models():
    return MODELS