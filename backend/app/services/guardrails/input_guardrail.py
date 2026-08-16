import re
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

UNSAFE_KEYWORDS = [
    "drop database", "sudo rm", "<script>", "ignore previous instructions", "jailbreak", "DAN mode"
]

class InputGuardrail:
    """Level 1 Guardrail: Validates input length, emptiness, off-topic, and safety violations."""
    
    def validate(self, query: str) -> Tuple[bool, str, str]:
        if not query or not query.strip():
            return False, "Query is empty or invalid.", ""

        clean_query = query.strip()
        
        if len(clean_query) < 3:
            return False, "Query is too short to process.", clean_query

        if len(clean_query) > 1000:
            return False, "Query exceeds maximum allowable character limit.", clean_query[:1000]

        lower_query = clean_query.lower()
        for kw in UNSAFE_KEYWORDS:
            if kw in lower_query:
                logger.warning(f"Unsafe/inappropriate input detected: {kw}")
                return False, "Input contains prohibited or unsafe instructions.", ""

        # Check for repetitive single-character gibberish (e.g. "aaaaaaa")
        if len(set(lower_query.replace(" ", ""))) < 2 and len(lower_query) > 10:
            return False, "Input appears to be invalid or gibberish.", ""

        return True, "Input validation passed.", clean_query

input_guardrail = InputGuardrail()
