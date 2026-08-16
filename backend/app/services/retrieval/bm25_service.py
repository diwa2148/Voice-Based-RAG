import os
import re
import pickle
import logging
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from backend.chunking.base import Chunk

logger = logging.getLogger(__name__)

class BM25Service:
    """Manages lexical keyword retrieval using BM25Okapi with persistent disk indexing."""
    
    def __init__(self, index_path: str = "bm25_index.pkl"):
        self.index_path = index_path
        self.bm25: Optional[BM25Okapi] = None
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.load_index()

    def _tokenize(self, text: str) -> List[str]:
        """Simple multilingual whitespace/alphanumeric tokenizer."""
        clean = text.lower().strip()
        # Keep Unicode letters, digits, and Indian language characters
        tokens = re.findall(r'\w+', clean)
        return tokens if tokens else [clean]

    def build_index(self, chunks: List[Chunk]):
        """Builds BM25 index from a list of Chunk objects."""
        if not chunks:
            return

        self.corpus_chunks = []
        tokenized_corpus = []

        for c in chunks:
            chunk_dict = {
                "chunk_id": c.chunk_id,
                "text": c.text,
                "chunking_strategy": c.chunking_strategy,
                "metadata": c.metadata
            }
            self.corpus_chunks.append(chunk_dict)
            tokenized_corpus.append(self._tokenize(c.text))

        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.save_index()
            logger.info(f"Built BM25 index over {len(chunks)} chunks.")

    def add_chunks(self, chunks: List[Chunk]):
        """Appends new chunks and rebuilds index."""
        all_chunks = []
        for d in self.corpus_chunks:
            all_chunks.append(
                Chunk(
                    chunk_id=d["chunk_id"],
                    text=d["text"],
                    chunking_strategy=d["chunking_strategy"],
                    metadata=d.get("metadata", {})
                )
            )
        all_chunks.extend(chunks)
        self.build_index(all_chunks)

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Searches BM25 index for keyword matches."""
        if not self.bm25 or not self.corpus_chunks:
            return []

        tokens = self._tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        max_score = float(max(scores)) if len(scores) > 0 and max(scores) > 0 else 1.0

        for idx in top_indices:
            score = float(scores[idx])
            if score > 0:
                item = self.corpus_chunks[idx].copy()
                # Normalize BM25 score to [0, 1] range for fusion
                item["score"] = float(round(score / max_score, 4))
                results.append(item)

        return results

    def save_index(self):
        try:
            with open(self.index_path, "wb") as f:
                pickle.dump({"corpus": self.corpus_chunks, "bm25": self.bm25}, f)
        except Exception as e:
            logger.error(f"Failed to save BM25 index to disk: {e}")

    def load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.corpus_chunks = data.get("corpus", [])
                    self.bm25 = data.get("bm25", None)
                    logger.info(f"Loaded existing BM25 index with {len(self.corpus_chunks)} passages.")
            except Exception as e:
                logger.warning(f"Could not load BM25 index from {self.index_path}: {e}")

bm25_service = BM25Service()
