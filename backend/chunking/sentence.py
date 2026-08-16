import re
from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class SentenceChunker(BaseChunker):
    """Splits text into chunks based on sentence boundaries, grouping sentences up to max_chunk_size."""
    
    def __init__(self, max_chunk_size: int = 400):
        self.max_chunk_size = max_chunk_size
        self.sentence_regex = re.compile(r'(?<=[.!?|।])\s+')

    @property
    def name(self) -> str:
        return "sentence"

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        meta = (metadata or {}).copy()
        meta["chunking_strategy"] = self.name
        chunks: List[Chunk] = []
        clean_text = text.strip()
        
        # Split sentences preserving punctuation
        sentences = [s.strip() for s in self.sentence_regex.split(clean_text) if s.strip()]
        if not sentences:
            sentences = [clean_text]

        current_sentences: List[str] = []
        current_len = 0
        start_char = 0
        idx = 0

        for sentence in sentences:
            s_len = len(sentence)
            if current_len + s_len > self.max_chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_sent_{idx}"
                chunks.append(
                    Chunk(
                        chunk_id=c_meta["chunk_id"],
                        text=chunk_text,
                        chunking_strategy=self.name,
                        start_char=start_char,
                        end_char=start_char + len(chunk_text),
                        token_count_approx=self.count_tokens_approx(chunk_text),
                        metadata=c_meta
                    )
                )
                idx += 1
                start_char += len(chunk_text) + 1
                current_sentences = [sentence]
                current_len = s_len
            else:
                current_sentences.append(sentence)
                current_len += s_len + 1

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            c_meta = meta.copy()
            c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_sent_{idx}"
            chunks.append(
                Chunk(
                    chunk_id=c_meta["chunk_id"],
                    text=chunk_text,
                    chunking_strategy=self.name,
                    start_char=start_char,
                    end_char=start_char + len(chunk_text),
                    token_count_approx=self.count_tokens_approx(chunk_text),
                    metadata=c_meta
                )
            )

        return chunks
