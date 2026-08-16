import re
from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class MetadataAwareChunker(BaseChunker):
    """Metadata-aware chunking strategy preserving structural headers, language tags, and passage metadata."""
    
    def __init__(self, target_chunk_size: int = 350):
        self.target_chunk_size = target_chunk_size

    @property
    def name(self) -> str:
        return "metadata_aware"

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        meta = (metadata or {}).copy()
        meta["chunking_strategy"] = self.name
        clean_text = text.strip()
        
        # Build contextual prefix from available metadata
        header_parts = []
        if "source" in meta:
            header_parts.append(f"[Source: {meta['source']}]")
        if "language" in meta:
            header_parts.append(f"[Lang: {meta['language']}]")
        if "query_id" in meta:
            header_parts.append(f"[QueryID: {meta['query_id']}]")
            
        header_prefix = " ".join(header_parts) + ("\n" if header_parts else "")

        # Split text into logical lines / paragraphs
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
        chunks: List[Chunk] = []
        current_lines: List[str] = []
        current_len = len(header_prefix)
        idx = 0
        start_char = 0

        for line in lines:
            line_len = len(line)
            if current_len + line_len > self.target_chunk_size and current_lines:
                body_text = "\n".join(current_lines)
                full_text = f"{header_prefix}{body_text}"
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_meta_{idx}"
                c_meta["has_metadata_header"] = bool(header_parts)
                chunks.append(
                    Chunk(
                        chunk_id=c_meta["chunk_id"],
                        text=full_text,
                        chunking_strategy=self.name,
                        start_char=start_char,
                        end_char=start_char + len(full_text),
                        token_count_approx=self.count_tokens_approx(full_text),
                        metadata=c_meta
                    )
                )
                idx += 1
                start_char += len(body_text) + 1
                current_lines = [line]
                current_len = len(header_prefix) + line_len
            else:
                current_lines.append(line)
                current_len += line_len + 1

        if current_lines:
            body_text = "\n".join(current_lines)
            full_text = f"{header_prefix}{body_text}"
            c_meta = meta.copy()
            c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_meta_{idx}"
            c_meta["has_metadata_header"] = bool(header_parts)
            chunks.append(
                Chunk(
                    chunk_id=c_meta["chunk_id"],
                    text=full_text,
                    chunking_strategy=self.name,
                    start_char=start_char,
                    end_char=start_char + len(full_text),
                    token_count_approx=self.count_tokens_approx(full_text),
                    metadata=c_meta
                )
            )

        return chunks
