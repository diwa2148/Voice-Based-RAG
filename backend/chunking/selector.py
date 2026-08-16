from typing import Dict, Any, Optional
from backend.chunking.base import BaseChunker
from backend.chunking.fixed_size import FixedSizeChunker
from backend.chunking.fixed_overlap import FixedOverlapChunker
from backend.chunking.sentence import SentenceChunker
from backend.chunking.paragraph import ParagraphChunker
from backend.chunking.recursive import RecursiveChunker
from backend.chunking.semantic import SemanticChunker
from backend.chunking.metadata_aware import MetadataAwareChunker

class AutoChunkingSelector:
    """Automatically selects the best chunking strategy based on text & metadata characteristics."""
    
    @staticmethod
    def select_strategy(text: str, metadata: Optional[Dict[str, Any]] = None) -> BaseChunker:
        meta = metadata or {}
        text_len = len(text)
        
        # 1. Check if metadata tags (source, language, query_id) are present
        if "source" in meta or "language" in meta or "query_id" in meta:
            return MetadataAwareChunker()
            
        # 2. Check paragraph structure
        if "\n\n" in text or "\r\n\r\n" in text:
            num_paragraphs = len(text.split("\n\n"))
            if num_paragraphs >= 3 and text_len > 600:
                return ParagraphChunker()
            return RecursiveChunker()
            
        # 3. Check sentence density
        num_sentences = len([s for s in text.split(".") if len(s.strip()) > 10])
        if num_sentences >= 4 and text_len > 400:
            return SemanticChunker()
        elif num_sentences >= 2:
            return SentenceChunker()
            
        # 4. Short / uniform text
        if text_len <= 300:
            return FixedSizeChunker()
            
        # Default strategy
        return FixedOverlapChunker()
