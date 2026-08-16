import os
import time
import logging
import hashlib
import numpy as np
import httpx
from typing import List, Union, Dict
from functools import lru_cache
from backend.app.config import settings

logger = logging.getLogger(__name__)

class BGEEmbeddingService:
    """API-first BAAI BGE-M3 embedding service with LRU caching and graceful offline fallback."""
    
    def __init__(self):
        self.api_url = settings.EMBEDDING_API_URL
        self.hf_token = settings.HF_TOKEN
        self.dimension = settings.EMBEDDING_DIMENSION  # Default 1024 for BGE-M3
        self._cache: Dict[str, List[float]] = {}
        self.max_cache_size = 2000
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=8.0)
        return self._client

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.strip().encode("utf-8")).hexdigest()

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generates a deterministic 1024-dim unit vector fallback when offline or API is unavailable."""
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    async def get_embedding_async(self, text: str) -> List[float]:
        """Asynchronously fetches BGE-M3 embedding vector for input text."""
        clean_text = text.strip()
        if not clean_text:
            return [0.0] * self.dimension

        cache_key = self._get_cache_key(clean_text)
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        try:
            client = self._get_client()
            response = await client.post(
                self.api_url,
                json={"inputs": clean_text, "options": {"wait_for_model": True}},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                # Hugging Face Feature Extraction API returns array of floats or nested array
                if isinstance(data, list):
                    if len(data) > 0 and isinstance(data[0], list):
                        # Token level embeddings; mean pool
                        vec = np.mean(np.array(data[0]), axis=0).tolist()
                    else:
                        vec = [float(x) for x in data]
                    
                    # Ensure dimension match
                    if len(vec) == self.dimension:
                        if len(self._cache) < self.max_cache_size:
                            self._cache[cache_key] = vec
                        return vec
        except Exception as e:
            logger.warning(f"Embedding API call failed: {e}. Utilizing fallback embedding generation.")

        # Fallback if API fails or token is missing
        fallback_vec = self._generate_fallback_embedding(clean_text)
        if len(self._cache) < self.max_cache_size:
            self._cache[cache_key] = fallback_vec
        return fallback_vec

    def get_embedding(self, text: str) -> List[float]:
        """Synchronous wrapper for embedding generation."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If running inside event loop
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.get_embedding_async(text))
            return loop.run_until_complete(self.get_embedding_async(text))
        except Exception:
            return asyncio.run(self.get_embedding_async(text))

    async def get_embeddings_batch_async(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of texts."""
        return [await self.get_embedding_async(t) for t in texts]

bge_embedder = BGEEmbeddingService()
