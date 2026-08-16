from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class FixedSizeChunker(BaseChunker):
    """Splits text into fixed character length chunks without overlap."""
    
    def __init__(self, chunk_size: int = 300):
        self.chunk_size = max(50, chunk_size)

    @property
    def name(self) -> str:
        return "fixed_size"

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
        while start < total_len:
            end = min(start + self.chunk_size, total_len)
            chunk_text = clean_text[start:end].strip()
            if chunk_text:
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_fs_{idx}"
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
            start = end
            
        return chunks
