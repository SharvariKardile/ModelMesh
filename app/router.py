from app.model_registry import get_models
from app.health import get_model_health

WEIGHTS = {
    "low": {
        "quality": 0.2,
        "latency": 0.3,
        "cost": 0.5
    },
    "medium": {
        "quality": 0.5,
        "latency": 0.25,
        "cost": 0.25
    },
    "high": {
        "quality": 0.8,
        "latency": 0.1,
        "cost": 0.1
    }
  
}
MIN_QUALITY = {
    "low": 0.90,
    "medium": 0.93,
    "high": 0.95
}

def calculate_model_score(model, weights, max_latency, max_cost):

    quality = model["quality"]

    normalized_latency = model["latency"] / max_latency

    normalized_cost = model["cost"] / max_cost

    score = (
        weights["quality"] * quality
        - weights["latency"] * normalized_latency
        - weights["cost"] * normalized_cost
    )

    return round(score, 4)


def select_model(complexity: str):

    models = get_models()
    health_status = get_model_health()

    weights = WEIGHTS[complexity]
    minimum_quality = MIN_QUALITY[complexity]

    # Step 1: Keep only healthy models
    healthy_models = [
        model for model in models
        if health_status[model["name"]]["healthy"]
    ]

    # Safety check
    if not healthy_models:
        raise RuntimeError("No healthy models available")

    # Step 2: Among healthy models, keep models
    # that meet the minimum quality requirement
    eligible_models = [
        model for model in healthy_models
        if model["quality"] >= minimum_quality
    ]

    # Safety fallback:
    # If no healthy model meets the quality requirement,
    # use all healthy models
    if not eligible_models:
        eligible_models = healthy_models

    # Step 3: Find maximum values for normalization
    max_latency = max(
        model["latency"] for model in eligible_models
    )

    max_cost = max(
        model["cost"] for model in eligible_models
    )

    # Step 4: Calculate routing score
    best_model = None
    best_score = float("-inf")

    for model in eligible_models:

        score = calculate_model_score(
            model,
            weights,
            max_latency,
            max_cost
        )

        if score > best_score:
            best_score = score
            best_model = model

    # Step 5: Return selected model
    return {
        **best_model,
        "routing_score": best_score,
        "minimum_quality": minimum_quality
    }