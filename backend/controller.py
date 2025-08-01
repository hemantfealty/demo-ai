from fastapi import APIRouter, HTTPException, Request, status, Query
from fastapi import HTTPException
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
from service import execute_query, search_messages_for_session
from agents import generate_query, generate_response, generate_chat_title, generate_questions_from_llm
from qdrant_client.http import models as rest
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import mysql.connector
import sqlparse
import tempfile
from fastapi import UploadFile, File

 
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
 
 
@router.get("/chats/{session_id}/search")
def search_chat_messages(
    session_id: str,
    query: str = Query(..., description="Search term for chat messages"),
    request: Request = None
):
    client = request.app.state.qdrant_client
    results = search_messages_for_session(client, session_id, query)
    return format_response(
        status_str="success",
        code=status.HTTP_200_OK,
        message="Search results",
        data={"messages": results},
    )
 
 
@router.get("/recommended-question")
def recommend_question(request: Request):
    schema_info = getattr(request.app.state, "schema_info", None)
    if schema_info is None:
        raise HTTPException(status_code=500, detail="Schema information not available")
    questions = generate_questions_from_llm(schema_info)
 
    return format_response(
        status_str="success",
        code=200,
        message="Generated suggested questions",
        data={"questions": questions}
    )

def search_messages_globally(client, query):
    all_sessions = get_all_sessions(client)
    all_messages = []
    for session in all_sessions:
        session_id = session["session_id"]
        messages = get_messages_for_session(client, session_id)
        # Add session_id to each message
        for m in messages:
            m_with_session = m.copy()
            m_with_session["session_id"] = session_id
            all_messages.append(m_with_session)
    return [m for m in all_messages if query.lower() in m["content"].lower()]

@router.get("/chats/search")
def search_all_chats(
    query: str = Query(..., description="Search term for chat messages"),
    request: Request = None
):
    client = request.app.state.qdrant_client
    results = search_messages_globally(client, query)
    return format_response(
        status_str="success",
        code=status.HTTP_200_OK,
        message="Global search results",
        data={"messages": results},
    )



# Helper function to backup a single table using Python only
def backup_table(table_name, db_config, backup_dir):
    try:
        backup_file = f"{backup_dir}/{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        create_table_sql = cursor.fetchone()[1]
        
        # Get table data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [column[0] for column in cursor.fetchall()]
        
        # Write to file
        with open(backup_file, "w", encoding="utf-8") as f:
            # Write table structure
            f.write(f"-- Table structure for {table_name}\n")
            f.write(f"{create_table_sql};\n\n")
            
            # Write data
            if rows:
                f.write(f"-- Data for {table_name}\n")
                for row in rows:
                    # Escape values properly
                    escaped_values = []
                    for value in row:
                        if value is None:
                            escaped_values.append("NULL")
                        elif isinstance(value, str):
                            escaped_values.append(f"'{value.replace(chr(39), chr(39)+chr(39))}'")
                        else:
                            escaped_values.append(str(value))
                    
                    f.write(f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])}) VALUES ({', '.join(escaped_values)});\n")
        
        cursor.close()
        conn.close()
        
        return {"table": table_name, "status": "success", "file": backup_file}
    except Exception as e:
        return {"table": table_name, "status": "error", "error": str(e)}

# Endpoint for direct database backup with parallel processing
@router.post("/backup-database-parallel")
def backup_database_parallel():
    # DB config from env vars
    db_config = {
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "database": os.getenv("MYSQL_DATABASE")
    }
    
    # Create backup directory
    backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        # Get list of all tables
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        # Backup tables in parallel
        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_table = {
                executor.submit(backup_table, table, db_config, backup_dir): table 
                for table in tables
            }
            
            for future in as_completed(future_to_table):
                table = future_to_table[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"table": table, "status": "error", "error": str(exc)}
                results.append(result)
        
        # Create a summary file
        summary_file = f"{backup_dir}/backup_summary.json"
        with open(summary_file, "w") as f:
            json.dump({
                "backup_timestamp": datetime.now().isoformat(),
                "database": db_config["database"],
                "total_tables": len(tables),
                "results": results
            }, f, indent=2)
        
        return format_response(
            status_str="success",
            code=status.HTTP_200_OK,
            message="Database backup completed",
            data={
                "backup_directory": backup_dir,
                "total_tables": len(tables),
                "results": results,
                "summary_file": summary_file
            }
        )
        
    except Exception as e:
        return format_response(
            status_str="error",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Backup failed",
            data={"error": str(e)}
        )

