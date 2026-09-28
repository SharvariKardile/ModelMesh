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
# Metrics Helper Functions
# ==================================================

def safe_record_success(start_time):

    try:
        record_success(start_time)

    except TypeError:
        record_success()


def safe_record_failure(start_time):

    try:
        record_failure(start_time)

    except TypeError:
        record_failure()


# ==================================================
# HOME ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "ModelMesh is running!",
        "version": "1.0.0"
    }


# ==================================================
# GENERATE ENDPOINT
# ==================================================

@app.post("/generate")
def generate(request: QueryRequest):

    start_time = time()

    # --------------------------------------------------
    # Step 1: Analyze query
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
        # Successful response
        # --------------------------------------------------

        if result["status"] == "success":

            attempts.append({

                "model": model["name"],

                "provider": model["provider"],

                "provider_model": model["provider_model"],

                "route_type": model["route_type"],

                "status": "success"

            })

            safe_record_success(
                start_time
            )

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
        # Model failed
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

    safe_record_failure(
        start_time
    )

    return {

        "query": request.query,

        "analysis": analysis,

        "selected_model": None,

        "response": (
            "All available AI providers "
            "are currently unavailable."
        ),

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

    complexity = analysis["complexity"]

    # --------------------------------------------------
    # Step 2: Rank models
    # --------------------------------------------------

    routing = rank_models(
        complexity
    )

    # --------------------------------------------------
    # Step 3: Build routing details
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
    # Step 4: Identify primary and fallback models
    # --------------------------------------------------

    primary_models = [

        model

        for model in routing

        if model["route_type"] == "primary"

    ]

    fallback_models = [

        model

        for model in routing

        if model["route_type"] == "fallback"

    ]

    # --------------------------------------------------
    # Step 5: Explain routing decision
    # --------------------------------------------------

    if complexity == "high":

        primary_reason = (
            "High-complexity queries require a model "
            "that meets the high quality threshold."
        )

        fallback_reason = (
            "Lower-ranked healthy models are retained "
            "as fallback options for fault tolerance."
        )

    elif complexity == "medium":

        primary_reason = (
            "Medium-complexity queries require a "
            "balanced quality, latency, and cost trade-off."
        )

        fallback_reason = (
            "Additional healthy models are retained "
            "as fallback options."
        )

    else:

        primary_reason = (
            "Low-complexity queries prioritize "
            "cost and latency efficiency."
        )

        fallback_reason = (
            "Additional healthy models are retained "
            "as fallback options."
        )

    # --------------------------------------------------
    # Step 6: Return complete routing decision
    # --------------------------------------------------

    return {

        "query": request.query,

        "analysis": analysis,

        "routing": routing_details,

        "routing_decision": {

            "primary_model": (

                primary_models[0]["name"]

                if primary_models

                else None

            ),

            "fallback_model": (

                fallback_models[0]["name"]

                if fallback_models

                else None

            ),

            "primary_reason": primary_reason,

            "fallback_reason": fallback_reason

        }

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