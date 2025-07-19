from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List, Dict
import uuid
from datetime import datetime

COLLECTION_NAME = "chat_messages"
VECTOR_SIZE = 128

def get_all_sessions(client: QdrantClient) -> List[Dict[str, str]]:
    session_data = {}
    next_offset = None
    while True:
        response = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="message_type",
                        match=rest.MatchValue(value="session_start")
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
            offset=next_offset
        )
        points, next_offset = response
        for point in points:
            session_id = point.payload["session_id"]
            title = point.payload.get("title", "new chat")  # Fallback to "new chat" if title is missing
            session_data[session_id] = {"session_id": session_id, "title": title}
        if next_offset is None:
            break
    return list(session_data.values())

def get_messages_for_session(client: QdrantClient, session_id: str) -> List[Dict]:
    response = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=rest.Filter(must=[rest.FieldCondition(key="session_id", match=rest.MatchValue(value=session_id))]),
        limit=1000,
        with_payload=True,
        with_vectors=False
    )
    points = response[0]
    messages = [point.payload for point in points]
    messages.sort(key=lambda x: x["timestamp"])
    return [{"type": m["message_type"], "content": m["content"], "timestamp": m["timestamp"]} for m in messages]

def delete_session(client: QdrantClient, session_id: str) -> bool:
    count_response = client.count(
        collection_name=COLLECTION_NAME,
        count_filter=rest.Filter(must=[rest.FieldCondition(key="session_id", match=rest.MatchValue(value=session_id))])
    )
    if count_response.count == 0:
        return False
    client.delete_points(
        collection_name=COLLECTION_NAME,
        points_selector=rest.Filter(must=[rest.FieldCondition(key="session_id", match=rest.MatchValue(value=session_id))])
    )
    return True

def get_chat_history(client: QdrantClient, session_id: str) -> List[Dict]:
    response = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=rest.Filter(
            must=[
                rest.FieldCondition(
                    key="session_id",
                    match=rest.MatchValue(value=session_id)
                ),
                rest.FieldCondition(
                    key="message_type",
                    match=rest.MatchAny(any=["user", "assistant"])
                )
            ]
        ),
        limit=1000,
        with_payload=True,
        with_vectors=False
    )
    points = response[0]
    messages = [point.payload for point in points]
    messages.sort(key=lambda x: x["timestamp"])
    return messages

def store_message(client: QdrantClient, message: dict):
    point_id = str(uuid.uuid4())
    vector = [0.0] * VECTOR_SIZE
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            rest.PointStruct(
                id=point_id,
                vector=vector,
                payload=message
            )
        ]
    )

def get_session_title(client: QdrantClient, session_id: str) -> str:
    response = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=rest.Filter(
            must=[
                rest.FieldCondition(
                    key="session_id",
                    match=rest.MatchValue(value=session_id)
                ),
                rest.FieldCondition(
                    key="message_type",
                    match=rest.MatchValue(value="session_start")
                )
            ]
        ),
        limit=1,
        with_payload=True,
        with_vectors=False
    )
    points = response[0]
    if points:
        return points[0].payload.get("title", "new chat")
    return "new chat"  # Fallback if session_start record is missing