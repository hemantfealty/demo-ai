from fastapi import FastAPI
from controller import router as database_router
from service import get_schema_info
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

app = FastAPI()

app.include_router(database_router)

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "chat_messages"
VECTOR_SIZE = 128

def init_qdrant():
    client = QdrantClient(url=QDRANT_URL)
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=rest.VectorParams(size=VECTOR_SIZE, distance=rest.Distance.COSINE)
        )
    return client

@app.get('/')
def startup_event():
    # Initialize schema info
    schema_info = get_schema_info()
    if schema_info is None:
        print("Warning: Could not retrieve schema information on startup")
    else:
        app.state.schema_info = schema_info
        print("Schema information retrieved successfully")
    
    # Initialize Qdrant client and store in app.state
    app.state.qdrant_client = init_qdrant()
    print("Qdrant collection initialized")

startup_event()