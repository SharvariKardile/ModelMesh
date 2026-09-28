from fastapi import FastAPI
from pydantic import BaseModel
from time import time

from app.analyzer import analyze_query
from app.router import rank_models
from app.model_client import generate_response
from app.metrics import (
    get_metrics,
    record_success,
    record_failure
)


# ==================================================
# ModelMesh Application
# ==================================================

app = FastAPI(
    title="ModelMesh",
    description="Intelligent Multi-Model AI Gateway",
    version="1.0.0"
)


# ==================================================
# Request Model
# ==================================================

class QueryRequest(BaseModel):
    query: str


# ==================================================
# Helper Functions
# ==================================================

def safe_record_success(start_time):
    """
    Record a successful request.

    Supports the current metrics implementation
    whether it expects a response time or no argument.
    """

    try:
        record_success(start_time)
    except TypeError:
        record_success()


def safe_record_failure(start_time):
    """
    Record a failed request.

    Supports the current metrics implementation
    whether it expects a response time or no argument.
    """

    try:
        record_failure(start_time)
    except TypeError:
        record_failure()


# ==================================================
# Home Endpoint
# ==================================================

@app.get("/")
def home():

    return {
        "message": "ModelMesh is running!",
        "version": "1.0.0"
    }


# ==================================================
# Generate Endpoint
# ==================================================

@app.post("/generate")
def generate(request: QueryRequest):

    start_time = time()

    # --------------------------------------------------
    # Step 1: Analyze the query
    # --------------------------------------------------

    analysis = analyze_query(
        request.query
    )

    complexity = analysis["complexity"]

    # --------------------------------------------------
    # Step 2: Rank models
    # --------------------------------------------------

    routing = rank_models(
        complexity
    )

    attempts = []

    # --------------------------------------------------
    # Step 3: Try models in ranked order
    # --------------------------------------------------

    for model in routing:

        result = generate_response(
            model,
            request.query
        )

        # --------------------------------------------------
        # Successful model response
        # --------------------------------------------------

        if result["status"] == "success":

            attempts.append({
                "model": model["name"],
                "provider": model["provider"],
                "provider_model": model["provider_model"],
                "route_type": model["route_type"],
                "status": "success"
            })

            safe_record_success(start_time)

            return {
                "query": request.query,

                "analysis": analysis,

                "selected_model": {
                    "name": model["name"],
                    "provider": model["provider"],
                    "provider_model": model["provider_model"],
                    "route_type": model["route_type"]
                },

                "response": result["response"],

                "attempts": attempts,

                "status": "success"
            }

        # --------------------------------------------------
        # Model failed -> try next model
        # --------------------------------------------------

        attempts.append({
            "model": model["name"],
            "provider": model["provider"],
            "provider_model": model["provider_model"],
            "route_type": model["route_type"],
            "status": "error",
            "error": result.get("error")
        })

    # --------------------------------------------------
    # All models failed
    # --------------------------------------------------

    safe_record_failure(start_time)

    return {
        "query": request.query,

        "analysis": analysis,

        "selected_model": None,

        "response": "All available AI providers are currently unavailable.",

        "attempts": attempts,

        "status": "all_models_failed"
    }


# ==================================================
# ROUTING DEMO ENDPOINT
# ==================================================

@app.post("/route")
def route_query(request: QueryRequest):

    # --------------------------------------------------
    # Step 1: Analyze query
    # --------------------------------------------------

    analysis = analyze_query(
        request.query
    )

    # --------------------------------------------------
    # Step 2: Rank models
    # --------------------------------------------------

    routing = rank_models(
        analysis["complexity"]
    )

    # --------------------------------------------------
    # Step 3: Build clean routing response
    # --------------------------------------------------

    routing_details = []

    for model in routing:

        routing_details.append({

            "model": model["name"],

            "provider": model["provider"],

            "provider_model": model["provider_model"],

            "route_type": model["route_type"],

            "routing_score": model["routing_score"]

        })

    # --------------------------------------------------
    # Step 4: Return routing decision
    # --------------------------------------------------

    return {

        "query": request.query,

        "analysis": analysis,

        "routing": routing_details

    }


# ==================================================
# HEALTH ENDPOINT
# ==================================================

@app.get("/health")
def health():

    from app.health import get_model_health

    health_status = get_model_health()

    # --------------------------------------------------
    # Count healthy models
    # --------------------------------------------------

    healthy_models = sum(
        1
        for model in health_status.values()
        if model["healthy"]
    )

    total_models = len(
        health_status
    )

    # --------------------------------------------------
    # Determine gateway status
    # --------------------------------------------------

    if healthy_models == total_models:

        gateway_status = "healthy"

    elif healthy_models > 0:

        gateway_status = "degraded"

    else:

        gateway_status = "unhealthy"

    # --------------------------------------------------
    # Return health information
    # --------------------------------------------------

    return {

        "gateway_status": gateway_status,

        "healthy_models": healthy_models,

        "total_models": total_models,

        "models": health_status

    }


# ==================================================
# METRICS ENDPOINT
# ==================================================

@app.get("/metrics")
def metrics():

    return get_metrics()