from typing import Dict, Any, Optional, List
from backend.chunking.base import BaseChunker, Chunk
from backend.chunking.fixed_size import FixedSizeChunker
from backend.chunking.fixed_overlap import FixedOverlapChunker
from backend.chunking.sentence import SentenceChunker
from backend.chunking.paragraph import ParagraphChunker
from backend.chunking.recursive import RecursiveChunker
from backend.chunking.semantic import SemanticChunker
from backend.chunking.metadata_aware import MetadataAwareChunker
from backend.chunking.selector import AutoChunkingSelector

STRATEGY_MAP: Dict[str, BaseChunker] = {
    "fixed_size": FixedSizeChunker(),
    "fixed_overlap": FixedOverlapChunker(),
    "sentence": SentenceChunker(),
    "paragraph": ParagraphChunker(),
    "recursive": RecursiveChunker(),
    "semantic": SemanticChunker(),
    "metadata_aware": MetadataAwareChunker(),
}

def get_chunker(strategy_name: str = "auto", text: str = "", metadata: Optional[Dict[str, Any]] = None) -> BaseChunker:
    """Returns requested chunker strategy or auto-selects optimal strategy."""
    if strategy_name == "auto" or not strategy_name:
        return AutoChunkingSelector.select_strategy(text, metadata)
    
    clean_name = strategy_name.lower().strip()
    if clean_name not in STRATEGY_MAP:
        raise ValueError(f"Unknown chunking strategy: '{strategy_name}'. Available: {list(STRATEGY_MAP.keys())} + ['auto']")
        
    return STRATEGY_MAP[clean_name]

def chunk_text(text: str, strategy_name: str = "auto", metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
    """Helper to chunk text directly with named or auto strategy."""
    chunker = get_chunker(strategy_name, text, metadata)
    return chunker.chunk(text, metadata)
