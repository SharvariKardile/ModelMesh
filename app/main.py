from fastapi import FastAPI
from pydantic import BaseModel

from app.analyzer import analyze_query
from app.router import rank_models
from app.model_client import generate_response


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
# Generate endpoint
# --------------------------------------------------

@app.post("/generate")
def generate(request: QueryRequest):

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

    for model in ranked_models:

        result = generate_response(
            model,
            request.query
        )

        # Record every model attempt
        attempts.append({
            "model": model["name"],
            "status": result["status"],
            "error": result.get("error")
        })

        # --------------------------------------------------
        # If model succeeds, return its response
        # --------------------------------------------------

        if result["status"] == "success":

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

    return {
        "query": request.query,
        "analysis": analysis,
        "selected_model": None,
        "response": "All available AI providers are currently unavailable.",
        "attempts": attempts,
        "status": "all_models_failed"
    }