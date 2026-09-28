# ModelMesh — Intelligent Multi-Model AI Gateway

ModelMesh is an intelligent AI gateway that analyzes incoming user queries and dynamically selects an appropriate AI model based on query complexity, model quality, latency, cost, and health.

The project demonstrates concepts from Software Engineering, Machine Learning, MLOps, and Cloud Computing.

## Current Features

- FastAPI-based AI gateway
- Query complexity analysis
- Model registry
- Intelligent model routing
- Quality-based model filtering
- Health-aware routing
- Simulated model failure and automatic failover
- Real Gemini API integration
- Secure API-key management using environment variables

## Architecture

```text
User
  |
  v
FastAPI Gateway
  |
  v
Query Analyzer
  |
  v
Intelligent Router
  |
  +----------------------+
  |                      |
  v                      v
Model Health        Model Registry
  |                      |
  +----------+-----------+
             |
             v
       Selected Model
             |
             v
         Gemini API
             |
             v
        AI Response