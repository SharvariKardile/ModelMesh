from fastapi import FastAPI
from pydantic import BaseModel

from app.analyzer import analyze_query
from app.router import select_model
from app.model_client import generate_response


app = FastAPI(title="ModelMesh")


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {
        "message": "ModelMesh is running!"
    }


@app.post("/generate")
def generate(request: QueryRequest):

    # Step 1: Analyze the query
    analysis = analyze_query(request.query)

    # Step 2: Select the best available model
    selected_model = select_model(
        analysis["complexity"]
    )

    # Step 3: Generate a response using the selected model
    result = generate_response(
        selected_model,
        request.query
    )

    return {
        "query": request.query,
        "analysis": analysis,
        "selected_model": selected_model,
        "response": result["response"]
    }