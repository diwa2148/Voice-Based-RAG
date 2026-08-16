import os
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

class QdrantService:
    """Manages Qdrant vector storage and dense similarity search."""
    
    def __init__(self):
        from backend.app.config import settings
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self.qdrant_url = settings.QDRANT_URL
        self.qdrant_api_key = settings.QDRANT_API_KEY
        self.storage_dir = settings.QDRANT_STORAGE_DIR
        self._init_client()

    def _init_client(self):
        if self.qdrant_url and self.qdrant_url.startswith("http"):
            logger.info(f"Connecting to remote Qdrant service at {self.qdrant_url}")
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key
            )
        else:
            os.makedirs(self.storage_dir, exist_ok=True)
            logger.info(f"Initializing local persistent Qdrant at {self.storage_dir}")
            self.client = QdrantClient(path=self.storage_dir)

        self.ensure_collection()

    def ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                logger.info(f"Creating Qdrant collection '{self.collection_name}' with vector size {self.dimension}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
                )
        except Exception as e:
            logger.error(f"Failed to verify/create Qdrant collection: {e}")

    def upsert_chunks(self, chunks: List[Any], vectors: List[List[float]]) -> int:
        if not chunks or not vectors or len(chunks) != len(vectors):
            return 0

        points = []
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id = hash(chunk.chunk_id) & 0x7FFFFFFFFFFFFFFF
            payload = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "chunking_strategy": chunk.chunking_strategy,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "token_count_approx": chunk.token_count_approx,
                **chunk.metadata
            }
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return len(points)

    def search_dense(
        self,
        query_vector: List[float],
        top_k: int = 20,
        language_filter: Optional[str] = None,
        strategy_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query_filter = None
        conditions = []
        
        if language_filter:
            conditions.append(FieldCondition(key="language", match=MatchValue(value=language_filter)))
        if strategy_filter:
            conditions.append(FieldCondition(key="chunking_strategy", match=MatchValue(value=strategy_filter)))

        if conditions:
            query_filter = Filter(must=conditions)

        dense_results = []
        try:
            # Check Qdrant Client API version compatibility
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    query_filter=query_filter,
                    with_payload=True
                )
                points = getattr(response, "points", response)
                for point in points:
                    dense_results.append({
                        "chunk_id": point.payload.get("chunk_id", ""),
                        "text": point.payload.get("text", ""),
                        "score": float(getattr(point, "score", 0.0)),
                        "chunking_strategy": point.payload.get("chunking_strategy", "unknown"),
                        "metadata": {k: v for k, v in point.payload.items() if k not in ["text"]}
                    })
            elif hasattr(self.client, "search"):
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=query_filter,
                    with_payload=True
                )
                for res in results:
                    dense_results.append({
                        "chunk_id": res.payload.get("chunk_id", ""),
                        "text": res.payload.get("text", ""),
                        "score": float(res.score),
                        "chunking_strategy": res.payload.get("chunking_strategy", "unknown"),
                        "metadata": {k: v for k, v in res.payload.items() if k not in ["text"]}
                    })
            return dense_results
        except Exception as e:
            logger.error(f"Error during Qdrant vector search: {e}")
            return []

    def is_healthy(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

qdrant_service = QdrantService()
