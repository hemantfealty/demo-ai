from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import uuid
from datetime import datetime
from qdrant_service import get_chat_history, store_message, get_all_sessions, get_messages_for_session, delete_session
from service import execute_query
from agents import generate_query, generate_response
import json

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chats")
def create_chat(request: Request):
    session_id = str(uuid.uuid4())
    client = request.app.state.qdrant_client
    # Store a session start record in Qdrant
    session_message = {
        "session_id": session_id,
        "message_type": "session_start",
        "content": "Chat session started",
        "timestamp": datetime.now().isoformat()
    }
    store_message(client, session_message)
    return {"session_id": session_id}

@router.post("/chats/{session_id}/messages")
def send_message(
    session_id: str,
    payload: ChatRequest,
    request: Request,
):
    schema_info = getattr(request.app.state, "schema_info", None)
    if schema_info is None:
        raise HTTPException(status_code=500, detail="Schema information not available")

    client = request.app.state.qdrant_client
    schema_str = json.dumps(schema_info, indent=2)

    # Retrieve previous messages for context
    previous_messages = get_chat_history(client, session_id)
    chat_history = "\n".join([f"{msg['message_type']}: {msg['content']}" for msg in previous_messages])

    # Generate SQL query with context
    query = generate_query(schema_str, chat_history, payload.question)

    try:
        results = execute_query(query)
        results_str = json.dumps(results, indent=2)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}")

    # Generate response with context
    response = generate_response(chat_history, query, results_str)

    # Store user message and AI response
    user_message = {
        "session_id": session_id,
        "message_type": "user",
        "content": payload.question,
        "timestamp": datetime.now().isoformat()
    }
    assistant_message = {
        "session_id": session_id,
        "message_type": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    }
    store_message(client, user_message)
    store_message(client, assistant_message)

    return {"response": response}

@router.get("/chats")
def get_all_chats(request: Request):
    client = request.app.state.qdrant_client
    session_ids = get_all_sessions(client)
    return {"session_ids": session_ids}

@router.get("/chats/{session_id}/messages")
def get_chat_messages(session_id: str, request: Request):
    client = request.app.state.qdrant_client
    messages = get_messages_for_session(client, session_id)
    return {"messages": messages}

@router.delete("/chats/{session_id}")
def delete_chat_session(session_id: str, request: Request):
    client = request.app.state.qdrant_client
    if not delete_session(client, session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}