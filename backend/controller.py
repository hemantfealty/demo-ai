from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from datetime import datetime
from qdrant_service import (
    get_chat_history,
    store_message,
    get_all_sessions,
    get_messages_for_session,
    delete_session,
    get_session_title,
)
from service import execute_query
from agents import generate_query, generate_response, generate_chat_title
from qdrant_client.http import models as rest
import json

router = APIRouter()

class ChatRequest(BaseModel):
    question: str


def format_response(
    *,
    status_str: str,
    code: int,
    message: str,
    data: dict | list | None = None,
) -> JSONResponse:
    payload = {
        "status": status_str,
        "status_code": code,
        "message": message,
        "data": data or {},
    }
    return JSONResponse(status_code=code, content=payload)


@router.post("/chats")
def create_chat(request: Request):
    session_id = str(uuid.uuid4())
    client = request.app.state.qdrant_client

    session_message = {
        "session_id": session_id,
        "message_type": "session_start",
        "content": "Chat session started",
        "title": "new chat",
        "timestamp": datetime.now().isoformat(),
    }
    store_message(client, session_message)

    return format_response(
        status_str="success",
        code=status.HTTP_201_CREATED,
        message="Chat session created",
        data={"session_id": session_id},
    )


@router.post("/chats/{session_id}/messages")
def send_message(
    session_id: str,
    payload: ChatRequest,
    request: Request,
):
    schema_info = getattr(request.app.state, "schema_info", None)
    if schema_info is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schema information not available",
        )

    client = request.app.state.qdrant_client
    schema_str = json.dumps(schema_info, indent=2)

    # Build chat history
    previous_messages = get_chat_history(client, session_id)
    chat_history = "\n".join(
        f"{msg['message_type']}: {msg['content']}" for msg in previous_messages
    )

    # First user message? update title
    if not any(msg["message_type"] == "user" for msg in previous_messages):
        title = generate_chat_title(payload.question)
        resp = client.scroll(
            collection_name="chat_messages",
            scroll_filter=rest.Filter(
                must=[
                    rest.FieldCondition(key="session_id", match=rest.MatchValue(value=session_id)),
                    rest.FieldCondition(key="message_type", match=rest.MatchValue(value="session_start")),
                ]
            ),
            limit=1,
            with_payload=True,
            with_vectors=False,
        )
        if resp and resp[0]:
            point_id = resp[0][0].id
            client.set_payload(
                collection_name="chat_messages", payload={"title": title}, points=[point_id]
            )

    # Generate and execute query
    query = generate_query(schema_str, chat_history, payload.question)
    try:
        results = execute_query(query)
        results_str = json.dumps(results, indent=2)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error executing query: {e}",
        )

    response_text = generate_response(chat_history, query, results_str)

    # Store both messages
    now = datetime.now().isoformat()
    store_message(
        client,
        {"session_id": session_id, "message_type": "user", "content": payload.question, "timestamp": now},
    )
    store_message(
        client,
        {"session_id": session_id, "message_type": "assistant", "content": response_text, "timestamp": now},
    )

    return format_response(
        status_str="success",
        code=status.HTTP_200_OK,
        message="Message processed",
        data={"response": response_text},
    )


@router.get("/chats")
def get_all_chats(request: Request):
    client = request.app.state.qdrant_client
    sessions = get_all_sessions(client)
    return format_response(
        status_str="success",
        code=status.HTTP_200_OK,
        message="Fetched all chat sessions",
        data={"sessions": sessions},
    )


@router.get("/chats/{session_id}/messages")
def get_chat_messages(session_id: str, request: Request):
    client = request.app.state.qdrant_client
    title = get_session_title(client, session_id)
    all_messages = get_messages_for_session(client, session_id)
    messages = [m for m in all_messages if m["type"] in ["user", "assistant"]]

    return format_response(
        status_str="success",
        code=status.HTTP_200_OK,
        message="Fetched messages for session",
        data={"title": title, "messages": messages},
    )


@router.delete("/chats/{session_id}")
def delete_chat_session(session_id: str, request: Request):
    client = request.app.state.qdrant_client
    if not delete_session(client, session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    return format_response(
        status_str="success",
        code=status.HTTP_200_OK,
        message="Session deleted successfully",
    )
