from __future__ import annotations

from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.core.config import settings


class MemoryClient:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
        self.collection = settings.qdrant_collection
        self.ensure_collection()

    def ensure_collection(self) -> None:
        collections = {item.name for item in self.client.get_collections().collections}
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=settings.qdrant_vector_size, distance=Distance.COSINE),
            )

    def upsert_memory(self, vector: list[float], payload: dict[str, Any]) -> None:
        self.client.upsert(
            collection_name=self.collection,
            points=[PointStruct(id=str(uuid4()), vector=vector, payload=payload)],
        )

    def search_memory(self, vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        results = self.client.search(collection_name=self.collection, query_vector=vector, limit=limit)
        return [dict(item.payload or {}) for item in results]
