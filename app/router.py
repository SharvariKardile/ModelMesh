from app.model_registry import get_models
from app.health import get_model_health


# --------------------------------------------------
# Routing weights
# --------------------------------------------------

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


# --------------------------------------------------
# Minimum quality required for each complexity level
# --------------------------------------------------

MIN_QUALITY = {
    "low": 0.90,
    "medium": 0.93,
    "high": 0.95
}


# --------------------------------------------------
# Calculate routing score
# --------------------------------------------------

def calculate_model_score(
    model,
    weights,
    max_latency,
    max_cost
):

    quality = model["quality"]

    normalized_latency = (
        model["latency"] / max_latency
    )

    normalized_cost = (
        model["cost"] / max_cost
    )

    score = (
        weights["quality"] * quality
        - weights["latency"] * normalized_latency
        - weights["cost"] * normalized_cost
    )

    return round(score, 4)


# --------------------------------------------------
# Rank models for a query
# --------------------------------------------------

def rank_models(complexity: str):

    models = get_models()

    health_status = get_model_health()

    weights = WEIGHTS[complexity]

    minimum_quality = MIN_QUALITY[complexity]

    # --------------------------------------------------
    # Step 1: Keep only healthy models
    # --------------------------------------------------

    healthy_models = [
        model
        for model in models
        if health_status[model["name"]]["healthy"]
    ]

    # Safety check
    if not healthy_models:
        raise RuntimeError(
            "No healthy models available"
        )

    # --------------------------------------------------
    # Step 2: Separate primary and fallback models
    # --------------------------------------------------

    primary_models = [
        model
        for model in healthy_models
        if model["quality"] >= minimum_quality
    ]

    fallback_models = [
        model
        for model in healthy_models
        if model["quality"] < minimum_quality
    ]

    # --------------------------------------------------
    # Step 3: If no primary model exists,
    # use all healthy models as candidates
    # --------------------------------------------------

    if not primary_models:

        primary_models = healthy_models
        fallback_models = []

    # --------------------------------------------------
    # Step 4: Calculate normalization values
    # using all healthy candidates
    # --------------------------------------------------

    max_latency = max(
        model["latency"]
        for model in healthy_models
    )

    max_cost = max(
        model["cost"]
        for model in healthy_models
    )

    # --------------------------------------------------
    # Step 5: Score primary models
    # --------------------------------------------------

    ranked_primary = []

    for model in primary_models:

        score = calculate_model_score(
            model,
            weights,
            max_latency,
            max_cost
        )

        ranked_primary.append({
            **model,
            "routing_score": score,
            "minimum_quality": minimum_quality,
            "route_type": "primary"
        })

    # --------------------------------------------------
    # Step 6: Score fallback models
    # --------------------------------------------------

    ranked_fallback = []

    for model in fallback_models:

        score = calculate_model_score(
            model,
            weights,
            max_latency,
            max_cost
        )

        ranked_fallback.append({
            **model,
            "routing_score": score,
            "minimum_quality": minimum_quality,
            "route_type": "fallback"
        })

    # --------------------------------------------------
    # Step 7: Sort each group by routing score
    # --------------------------------------------------

    ranked_primary.sort(
        key=lambda model: model["routing_score"],
        reverse=True
    )

    ranked_fallback.sort(
        key=lambda model: model["routing_score"],
        reverse=True
    )

    # --------------------------------------------------
    # Step 8: Primary models always come first
    # Fallback models come after them
    # --------------------------------------------------

    ranked_models = (
        ranked_primary +
        ranked_fallback
    )

    return ranked_models


# --------------------------------------------------
# Select the first / best primary model
# --------------------------------------------------

def select_model(complexity: str):

    ranked_models = rank_models(complexity)

    return ranked_models[0]