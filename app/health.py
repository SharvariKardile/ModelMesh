from app.model_registry import get_models


def get_model_health():

    models = get_models()

    health_status = {}

    for model in models:

        # Simulated health status
        # Change a model's value to False to simulate failure
        if model["name"] == "Model-B":
            health_status[model["name"]] = {
                "healthy": False
            }
        else:
            health_status[model["name"]] = {
                "healthy": True
            }

    return health_status