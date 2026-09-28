from fastapi import FastAPI
from pydantic import BaseModel

from app.analyzer import analyze_query
from app.router import rank_models
from app.model_client import generate_response

from app.metrics import (
    start_timer,
    record_model_attempt,
    record_success,
    record_failure,
    get_metrics
)

from app.health import get_model_health


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(title="ModelMesh")


# --------------------------------------------------
# Request model
# --------------------------------------------------

class QueryRequest(BaseModel):
    query: str


# --------------------------------------------------
# Home endpoint
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "ModelMesh is running!"
    }


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():

    health_status = get_model_health()

    healthy_count = sum(
        1
        for model in health_status.values()
        if model["healthy"]
    )

    total_models = len(health_status)

    if healthy_count == total_models:
        gateway_status = "healthy"

    elif healthy_count > 0:
        gateway_status = "degraded"

    else:
        gateway_status = "unhealthy"

    return {
        "gateway_status": gateway_status,
        "healthy_models": healthy_count,
        "total_models": total_models,
        "models": health_status
    }


# --------------------------------------------------
# Generate endpoint
# --------------------------------------------------

@app.post("/generate")
def generate(request: QueryRequest):

    # Start request timer
    start_time = start_timer()

    # --------------------------------------------------
    # Step 1: Analyze the query
    # --------------------------------------------------

    analysis = analyze_query(
        request.query
    )

    # --------------------------------------------------
    # Step 2: Rank available models
    # --------------------------------------------------

    ranked_models = rank_models(
        analysis["complexity"]
    )

    # --------------------------------------------------
    # Step 3: Try models in ranked order
    # --------------------------------------------------

    attempts = []

    for index, model in enumerate(ranked_models):

        # Every attempt after the first one
        # is considered a fallback attempt
        is_fallback = index > 0

        # Record model attempt
        record_model_attempt(
            model["name"],
            is_fallback=is_fallback
        )

        # Call the selected model
        result = generate_response(
            model,
            request.query
        )

        # Store attempt information
        attempts.append({
            "model": model["name"],
            "status": result["status"],
            "error": result.get("error")
        })

        # --------------------------------------------------
        # If model succeeds
        # --------------------------------------------------

        if result["status"] == "success":

            record_success(start_time)

            return {
                "query": request.query,
                "analysis": analysis,
                "selected_model": model,
                "response": result["response"],
                "attempts": attempts,
                "status": "success"
            }

    # --------------------------------------------------
    # Step 4: All models failed
    # --------------------------------------------------

    record_failure(start_time)

    return {
        "query": request.query,
        "analysis": analysis,
        "selected_model": None,
        "response": "All available AI providers are currently unavailable.",
        "attempts": attempts,
        "status": "all_models_failed"
    }


# --------------------------------------------------
# Metrics endpoint
# --------------------------------------------------

@app.get("/metrics")
def metrics():

    return get_metrics()