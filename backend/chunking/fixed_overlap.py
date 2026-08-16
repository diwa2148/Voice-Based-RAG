from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class FixedOverlapChunker(BaseChunker):
    """Splits text into fixed length chunks with sliding window overlap."""
    
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = max(100, chunk_size)
        self.overlap = min(overlap, self.chunk_size // 2)

    @property
    def name(self) -> str:
        return "fixed_overlap"

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        meta = (metadata or {}).copy()
        meta["chunking_strategy"] = self.name
        chunks: List[Chunk] = []
        clean_text = text.strip()
        total_len = len(clean_text)
        
        start = 0
        idx = 0
        step = self.chunk_size - self.overlap
        
        while start < total_len:
            end = min(start + self.chunk_size, total_len)
            chunk_text = clean_text[start:end].strip()
            if chunk_text:
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_fo_{idx}"
                chunks.append(
                    Chunk(
                        chunk_id=c_meta["chunk_id"],
                        text=chunk_text,
                        chunking_strategy=self.name,
                        start_char=start,
                        end_char=end,
                        token_count_approx=self.count_tokens_approx(chunk_text),
                        metadata=c_meta
                    )
                )
                idx += 1
            if end >= total_len:
                break
            start += step
            
        return chunks
