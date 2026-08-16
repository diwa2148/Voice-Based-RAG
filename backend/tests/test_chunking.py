import pytest
from backend.chunking import get_chunker, chunk_text, STRATEGY_MAP
from backend.chunking.fixed_size import FixedSizeChunker
from backend.chunking.fixed_overlap import FixedOverlapChunker
from backend.chunking.sentence import SentenceChunker
from backend.chunking.paragraph import ParagraphChunker
from backend.chunking.recursive import RecursiveChunker
from backend.chunking.semantic import SemanticChunker
from backend.chunking.metadata_aware import MetadataAwareChunker
from backend.chunking.selector import AutoChunkingSelector

SAMPLE_TEXT = """
MS MARCO-XI is a multilingual retrieval dataset created for benchmarking information retrieval in Indian languages.
It contains queries and passages in multiple languages including Hindi, Bengali, Tamil, Telugu, and English.

Retrieval Augmented Generation (RAG) combines semantic retrieval with large language models to produce grounded answers.
By indexing passages into Qdrant vector database and BM25 index, hybrid retrieval delivers high accuracy.

The 7 chunking strategies ensure that text can be evaluated across different segment sizes and boundary awareness.
"""

def test_all_strategies_exist():
    assert len(STRATEGY_MAP) == 7
    for name in ["fixed_size", "fixed_overlap", "sentence", "paragraph", "recursive", "semantic", "metadata_aware"]:
        assert name in STRATEGY_MAP

def test_chunking_execution():
    meta = {"passage_id": "test_pass_1", "language": "hi", "source": "msmarco"}
    for name, chunker in STRATEGY_MAP.items():
        chunks = chunker.chunk(SAMPLE_TEXT, meta)
        assert len(chunks) > 0, f"Chunker {name} returned no chunks"
        for c in chunks:
            assert c.chunking_strategy == name
            assert c.text is not None and len(c.text) > 0
            assert "passage_id" in c.metadata

def test_auto_selector():
    # Test metadata-aware selection
    c_meta = AutoChunkingSelector.select_strategy("Sample text", {"source": "MSMARCO"})
    assert c_meta.name == "metadata_aware"

    # Test paragraph selection
    c_para = AutoChunkingSelector.select_strategy("Para 1 text...\n\nPara 2 text...\n\nPara 3 text...", {})
    assert c_para.name in ["paragraph", "recursive"]

    # Test factory with auto
    chunks = chunk_text(SAMPLE_TEXT, strategy_name="auto", metadata={"source": "test"})
    assert len(chunks) > 0
