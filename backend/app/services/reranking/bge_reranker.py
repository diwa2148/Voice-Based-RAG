import logging
import httpx
import numpy as np
from typing import List, Dict, Any
from backend.app.config import settings

logger = logging.getLogger(__name__)

class BGERerankerService:
    """API-first BGE CrossEncoder Reranker service with fallback scoring."""
    
    def __init__(self):
        self.api_url = settings.RERANKER_API_URL
        self.hf_token = settings.HF_TOKEN
        self.enabled = settings.ENABLE_RERANKER
        self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=8.0)
        return self._client

    def _fallback_rerank_score(self, query: str, text: str) -> float:
        """Computes lexical term overlap & length-normalized score fallback."""
        q_words = set(query.lower().split())
        t_words = set(text.lower().split())
        if not q_words or not t_words:
            return 0.0
        overlap = len(q_words & t_words) / len(q_words)
        return float(round(0.5 + (0.5 * overlap), 4))

    async def rerank_async(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Reranks candidate chunks based on relevance to query."""
        if not candidates or not self.enabled:
            return candidates[:top_k]

        texts = [c.get("text", "") for c in candidates]
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        reranked = []
        try:
            payload = {
                "inputs": [{"text": query, "text_pair": c.get("text", "")} for c in candidates]
            }
            client = self._get_client()
            response = await client.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            if response.status_code == 200:
                raw_res = response.json()
                # HF text classification returns list of lists or list of dicts with 'score'
                scores = []
                if isinstance(raw_res, list):
                    for item in raw_res:
                        if isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict):
                            scores.append(float(item[0].get("score", 0.0)))
                        elif isinstance(item, dict) and "score" in item:
                            scores.append(float(item["score"]))
                        elif isinstance(item, (int, float)):
                            scores.append(float(item))

                if len(scores) == len(candidates):
                    for idx, score_val in enumerate(scores):
                        c_item = candidates[idx].copy()
                        c_item["rerank_score"] = float(score_val)
                        c_item["score"] = float(score_val)
                        reranked.append(c_item)
                    
                    reranked = sorted(reranked, key=lambda x: x["rerank_score"], reverse=True)
                    return reranked[:top_k]
        except Exception as e:
            logger.warning(f"Reranker API call failed: {e}. Falling back to internal rerank heuristic.")

        # Fallback Reranking Heuristic
        for c in candidates:
            c_item = c.copy()
            fallback_score = self._fallback_rerank_score(query, c_item.get("text", ""))
            # Blend RRF score + fallback score
            combined_score = float(round((c_item.get("score", 0.0) * 0.5) + (fallback_score * 0.5), 4))
            c_item["rerank_score"] = combined_score
            c_item["score"] = combined_score
            reranked.append(c_item)

        reranked = sorted(reranked, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]

bge_reranker = BGERerankerService()
