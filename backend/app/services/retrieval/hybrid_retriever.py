import logging
from typing import List, Dict, Any, Optional
from backend.app.services.embeddings.bge_embedder import bge_embedder
from backend.app.services.retrieval.qdrant_service import qdrant_service
from backend.app.services.retrieval.bm25_service import bm25_service

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Combines Qdrant dense vector search and BM25 lexical keyword search via Reciprocal Rank Fusion (RRF)."""
    
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def fuse_results(
        self,
        dense_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """Fuses pre-computed dense and BM25 candidate lists via RRF."""
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Process Dense ranks
        for rank, item in enumerate(dense_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))
            if cid not in chunk_map:
                item_copy = item.copy()
                item_copy["retrieval_sources"] = ["dense"]
                item_copy["dense_score"] = item.get("score", 0.0)
                chunk_map[cid] = item_copy

        # Process BM25 ranks
        for rank, item in enumerate(bm25_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))
            if cid not in chunk_map:
                item_copy = item.copy()
                item_copy["retrieval_sources"] = ["bm25"]
                item_copy["bm25_score"] = item.get("score", 0.0)
                chunk_map[cid] = item_copy
            else:
                chunk_map[cid]["retrieval_sources"].append("bm25")
                chunk_map[cid]["bm25_score"] = item.get("score", 0.0)

        # Sort candidates by RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:top_k]

        candidates = []
        for cid in sorted_cids:
            c_info = chunk_map[cid]
            c_info["rrf_score"] = float(round(rrf_scores[cid], 5))
            c_info["score"] = float(round(rrf_scores[cid], 5))
            candidates.append(c_info)

        return candidates

    async def retrieve_async(
        self,
        query: str,
        top_k: int = 20,
        language_filter: Optional[str] = None,
        strategy_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes dense + BM25 retrieval and fuses results via RRF."""
        query_vector = await bge_embedder.get_embedding_async(query)

        dense_results = qdrant_service.search_dense(
            query_vector=query_vector,
            top_k=top_k,
            language_filter=language_filter,
            strategy_filter=strategy_filter
        )

        bm25_results = bm25_service.search(query, top_k=top_k)
        candidates = self.fuse_results(dense_results, bm25_results, top_k=top_k)

        return {
            "query": query,
            "dense_count": len(dense_results),
            "bm25_count": len(bm25_results),
            "candidates": candidates
        }

hybrid_retriever = HybridRetriever()
