from fastapi import FastAPI
from controller import router as database_router
from service import get_schema_info

app = FastAPI()

app.include_router(database_router)

@app.get('/')
def startup_event():
    schema_info = get_schema_info()
    if schema_info is None:
        print("Warning: Could not retrieve schema information on startup")
        return "Warning: Could not retrieve schema information on startup"
    else:
        app.state.schema_info = schema_info
        print("Schema information retrieved successfully")
        return "Schema information retrieved successfully"

startup_event()


# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field
# from uuid import uuid4
# from datetime import datetime
# from pathlib import Path
# import json
# import os
# from qdrant_client import QdrantClient
# from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain.vectorstores import Qdrant
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv
# from qdrant_client.http import models as rest

# load_dotenv()

# app = FastAPI()

# # Qdrant configuration
# QDRANT_URL = "http://localhost:6333"
# client = QdrantClient(url=QDRANT_URL)

# # Directory to store chat files
# CHAT_DIR = Path(__file__).parent / "chats"
# CHAT_DIR.mkdir(exist_ok=True)

# # Dummy user ID
# DUMMY_USER_ID = "9cc024e5-c451-4a7f-8a61-1e4de73664c9"

# # LangChain setup
# model = GoogleGenerativeAI(model="gemini-1.5-pro")
# embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")

# # Prompt template for QA chain
# prompt_template = PromptTemplate(
#     input_variables=["context", "question"],
#     template="Based on the following schema information, answer the question:\n{context}\n\nQuestion: {question}\nAnswer:"
# )

# # Initialize Qdrant vector store
# vectorstore = Qdrant(
#     client=client,
#     collection_name="SchemaInfo",
#     embeddings=embeddings
# )

# # Set up QA chain
# qa_chain = RetrievalQA.from_chain_type(
#     llm=model,
#     chain_type="stuff",
#     retriever=vectorstore.as_retriever(),
#     chain_type_kwargs={"prompt": prompt_template}
# )

# def now_iso():
#     return datetime.utcnow().isoformat(timespec="seconds")

# class CreateSessionRequest(BaseModel):
#     title: str

# class Session(BaseModel):
#     id: str
#     user_id: str
#     title: str
#     content: list = Field(default_factory=list)
#     created_at: str
#     updated_at: str
#     is_active: bool = True
#     message_count: int = 0

# class UpdateTitleRequest(BaseModel):
#     title: str

# class AddMessageRequest(BaseModel):
#     human_message: str
#     module: str  # Ignored in this implementation

# def session_file(session_id: str) -> Path:
#     return CHAT_DIR / f"{session_id}.json"

# def load_session(session_id: str) -> Session:
#     path = session_file(session_id)
#     if not path.exists():
#         raise HTTPException(status_code=404, detail="Session not found")
#     data = json.loads(path.read_text())
#     return Session(**data)

# def save_session(session: Session):
#     path = session_file(session.id)
#     path.write_text(session.json())

# @app.on_event("startup")
# def populate_schema_info():
#     # Delete existing collection if it exists
#     try:
#         client.delete_collection("SchemaInfo")
#     except:
#         pass
#     # Create SchemaInfo collection
#     client.create_collection(
#         collection_name="SchemaInfo",
#         vectors_config=rest.VectorParams(size=1536, distance=rest.Distance.COSINE)
#     )
#     # Placeholder schema (replace with your actual schema if available)
#     schema = {
#         "classes": [
#             {
#                 "class": "ExampleClass",
#                 "description": "An example class for demonstration",
#                 "properties": [
#                     {"name": "prop1", "dataType": ["string"], "description": "First property"},
#                     {"name": "prop2", "dataType": ["int"], "description": "Second property"}
#                 ]
#             }
#         ]
#     }
#     # Populate with data
#     points = []
#     for class_info in schema["classes"]:
#         class_name = class_info["class"]
#         class_description = class_info.get("description", "")
#         points.append(
#             rest.PointStruct(
#                 id=str(uuid4()),
#                 vector=embeddings.embed_query(class_description) if class_description else [0.0] * 1536,
#                 payload={"type": "class", "name": class_name, "description": class_description}
#             )
#         )
#         for prop in class_info["properties"]:
#             prop_name = prop["name"]
#             prop_description = prop.get("description", "")
#             prop_data_type = prop["dataType"]
#             points.append(
#                 rest.PointStruct(
#                     id=str(uuid4()),
#                     vector=embeddings.embed_query(
#                         f"Property {prop_name} of class {class_name}, data type: {prop_data_type}, description: {prop_description}"
#                     ) if prop_description else [0.0] * 1536,
#                     payload={
#                         "type": "property",
#                         "name": f"{class_name}.{prop_name}",
#                         "description": f"Property {prop_name} of class {class_name}, data type: {prop_data_type}, description: {prop_description}"
#                     }
#                 )
#             )
#     client.upsert(collection_name="SchemaInfo", points=points)

# @app.post("/chat-sessions/", status_code=201)
# def create_session(req: CreateSessionRequest):
#     session_id = str(uuid4())
#     now = now_iso()
#     session = Session(
#         id=session_id,
#         user_id=DUMMY_USER_ID,
#         title=req.title,
#         created_at=now,
#         updated_at=now,
#     )
#     save_session(session)
#     return {
#         "status": True,
#         "status_code": 201,
#         "message": "Chat session created successfully",
#         "data": session.dict()
#     }

# @app.get("/chat-sessions/user/me")
# def get_my_sessions():
#     sessions = []
#     for path in CHAT_DIR.glob("*.json"):
#         data = json.loads(path.read_text())
#         if data.get("user_id") == DUMMY_USER_ID:
#             sessions.append(data)
#     return {
#         "status": True,
#         "status_code": 200,
#         "message": "Chat sessions retrieved successfully",
#         "data": sessions
#     }

# @app.get("/chat-sessions/{session_id}")
# def get_session(session_id: str):
#     session = load_session(session_id)
#     return {
#         "status": True,
#         "status_code": 200,
#         "message": "Chat session retrieved successfully",
#         "data": session.dict()
#     }

# @app.delete("/chat-sessions/{session_id}")
# def delete_session(session_id: str):
#     path = session_file(session_id)
#     if not path.exists():
#         raise HTTPException(status_code=404, detail="Session not found")
#     path.unlink()
#     return {
#         "status": True,
#         "status_code": 200,
#         "message": "Chat session deleted successfully"
#     }

# @app.put("/chat-sessions/{session_id}/title")
# def update_title(session_id: str, req: UpdateTitleRequest):
#     session = load_session(session_id)
#     session.title = req.title
#     session.updated_at = now_iso()
#     save_session(session)
#     return {
#         "status": True,
#         "status_code": 200,
#         "message": "Session title updated successfully",
#         "data": session.dict()
#     }

# @app.post("/chat-sessions/{session_id}/messages")
# def add_message(session_id: str, req: AddMessageRequest):
#     session = load_session(session_id)
#     # Use QA chain to generate response
#     ai_response = qa_chain.run(req.human_message)
#     # Append human message and AI response
#     session.content.append({
#         "human": req.human_message,
#         "ai": ai_response
#     })
#     session.message_count = len(session.content)
#     session.updated_at = now_iso()
#     save_session(session)
#     return {
#         "status": True,
#         "status_code": 200,
#         "message": "Message added successfully",
#         "data": session.dict()
#     }

