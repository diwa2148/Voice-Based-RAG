import re
from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class ParagraphChunker(BaseChunker):
    """Splits text along paragraph breaks (double newlines)."""
    
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size
        self.para_regex = re.compile(r'\n\s*\n')

    @property
    def name(self) -> str:
        return "paragraph"

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        meta = (metadata or {}).copy()
        meta["chunking_strategy"] = self.name
        chunks: List[Chunk] = []
        clean_text = text.strip()
        
        paragraphs = [p.strip() for p in self.para_regex.split(clean_text) if p.strip()]
        if not paragraphs:
            paragraphs = [clean_text]

        current_paras: List[str] = []
        current_len = 0
        start_char = 0
        idx = 0

        for para in paragraphs:
            p_len = len(para)
            if current_len + p_len > self.max_chunk_size and current_paras:
                chunk_text = "\n\n".join(current_paras)
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_para_{idx}"
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
                start_char += len(chunk_text) + 2
                current_paras = [para]
                current_len = p_len
            else:
                current_paras.append(para)
                current_len += p_len + 2

        if current_paras:
            chunk_text = "\n\n".join(current_paras)
            c_meta = meta.copy()
            c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_para_{idx}"
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
