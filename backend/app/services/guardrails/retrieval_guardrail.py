import logging
from typing import List, Dict, Any, Tuple
from backend.app.config import settings

logger = logging.getLogger(__name__)

class RetrievalGuardrail:
    """Level 2 Guardrail: Inspects retrieval scores to ensure sufficient context grounding."""
    
    def __init__(self, min_score_threshold: float = None):
        self.min_score_threshold = min_score_threshold if min_score_threshold is not None else settings.MIN_RETRIEVAL_SCORE

    def validate(
        self,
        query: str,
        chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        if not chunks:
            return False, "No context chunks were retrieved from the knowledge base.", []

        # Filter out chunks below minimum score threshold
        valid_chunks = [c for c in chunks if c.get("score", 0.0) >= self.min_score_threshold]

        if not valid_chunks:
            # If no chunks exceed threshold, check top score
            top_score = chunks[0].get("score", 0.0) if chunks else 0.0
            logger.info(f"Retrieval Guardrail Triggered: Top retrieval score {top_score:.4f} is below threshold {self.min_score_threshold}")
            return False, f"Retrieved context relevance score ({top_score:.3f}) is below minimum grounding threshold.", []

        return True, "Sufficient relevant context retrieved.", valid_chunks

retrieval_guardrail = RetrievalGuardrail()
