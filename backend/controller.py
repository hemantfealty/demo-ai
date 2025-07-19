from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from service import execute_query
from agents import generate_query, generate_response
import json

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(
    payload: ChatRequest,
    request: Request,                      
):
    schema_info = getattr(request.app.state, "schema_info", None)
    if schema_info is None:
        raise HTTPException(status_code=500, detail="Schema information not available")

    schema_str = json.dumps(schema_info, indent=2)
    query = generate_query(schema_str, payload.question)

    try:
        results = execute_query(query)
        results_str = json.dumps(results, indent=2)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}")

    response = generate_response(query, results_str)
    return {"response": response}