from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class RecursiveChunker(BaseChunker):
    """Recursively splits text by structural separators ["\n\n", "\n", ". ", " ", ""]."""
    
    def __init__(self, chunk_size: int = 350, chunk_overlap: int = 40):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    @property
    def name(self) -> str:
        return "recursive"

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size or not separators:
            return [text] if text.strip() else []

        sep = separators[0]
        new_separators = separators[1:]

        if sep == "":
            # Character-level fallback
            splits = [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
            return [s for s in splits if s.strip()]

        parts = text.split(sep)
        final_chunks: List[str] = []
        current_chunk: List[str] = []
        current_length = 0

        for part in parts:
            part_len = len(part) + len(sep)
            if part_len > self.chunk_size:
                # Sub-part is too large; split with next separators
                if current_chunk:
                    final_chunks.append(sep.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                final_chunks.extend(self._split_text(part, new_separators))
            elif current_length + part_len > self.chunk_size and current_chunk:
                final_chunks.append(sep.join(current_chunk))
                current_chunk = [part]
                current_length = len(part)
            else:
                current_chunk.append(part)
                current_length += part_len

        if current_chunk:
            final_chunks.append(sep.join(current_chunk))

        return final_chunks

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        meta = (metadata or {}).copy()
        meta["chunking_strategy"] = self.name
        clean_text = text.strip()
        
        raw_splits = self._split_text(clean_text, self.separators)
        chunks: List[Chunk] = []
        idx = 0
        start_char = 0

        for split in raw_splits:
            chunk_text = split.strip()
            if chunk_text:
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_rec_{idx}"
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
                start_char += len(chunk_text)

        return chunks
