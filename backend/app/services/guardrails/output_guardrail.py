import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

CONTROLLED_REFUSAL = "I couldn't find enough relevant information in the provided knowledge base to answer that reliably."

class OutputGuardrail:
    """Level 3 Guardrail: Verifies generated answer against retrieved context to prevent hallucinations."""
    
    def validate(
        self,
        query: str,
        answer: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, str, bool]:
        if not answer or not answer.strip():
            return False, CONTROLLED_REFUSAL, True

        clean_answer = answer.strip()

        # Check if model already emitted refusal
        if "couldn't find enough" in clean_answer.lower() or "insufficient" in clean_answer.lower() or "not enough information" in clean_answer.lower():
            return True, CONTROLLED_REFUSAL, False

        if not context_chunks:
            return False, CONTROLLED_REFUSAL, True

        # Extract key words/entities from answer to verify overlap with context
        context_text = " ".join([c.get("text", "") for c in context_chunks]).lower()
        context_words = set(re.findall(r'\w+', context_text))

        answer_words = [w.lower() for w in re.findall(r'\w+', clean_answer) if len(w) > 4]
        
        if answer_words:
            matched_words = [w for w in answer_words if w in context_words]
            overlap_ratio = len(matched_words) / len(answer_words)

            if overlap_ratio < 0.25:
                logger.warning(f"Output Guardrail Hallucination Flagged: Low word overlap ratio ({overlap_ratio:.2f}) between answer and context.")
                return False, CONTROLLED_REFUSAL, True

        return True, clean_answer, False

output_guardrail = OutputGuardrail()
