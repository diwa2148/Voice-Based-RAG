import re
from typing import List, Dict, Any, Optional
from backend.chunking.base import BaseChunker, Chunk

class SemanticChunker(BaseChunker):
    """Semantic chunking strategy grouping sentences based on contextual similarity thresholds."""
    
    def __init__(self, target_chunk_size: int = 350, similarity_threshold: float = 0.4):
        self.target_chunk_size = target_chunk_size
        self.similarity_threshold = similarity_threshold
        self.sentence_regex = re.compile(r'(?<=[.!?|।])\s+')

    @property
    def name(self) -> str:
        return "semantic"

    def _word_set(self, text: str) -> set:
        return set(re.findall(r'\w+', text.lower()))

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        w1, w2 = self._word_set(text1), self._word_set(text2)
        if not w1 or not w2:
            return 0.0
        return len(w1 & w2) / len(w1 | w2)

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        meta = (metadata or {}).copy()
        meta["chunking_strategy"] = self.name
        clean_text = text.strip()
        
        sentences = [s.strip() for s in self.sentence_regex.split(clean_text) if s.strip()]
        if not sentences:
            sentences = [clean_text]

        chunks: List[Chunk] = []
        current_chunk_sentences: List[str] = [sentences[0]]
        current_len = len(sentences[0])
        idx = 0
        start_char = 0

        for i in range(1, len(sentences)):
            prev_sentence = sentences[i - 1]
            curr_sentence = sentences[i]
            sim = self._jaccard_similarity(prev_sentence, curr_sentence)
            s_len = len(curr_sentence)

            # Split if semantic shift detected AND chunk is large enough, or if chunk exceeds size limit
            if (sim < self.similarity_threshold and current_len >= 150) or (current_len + s_len > self.target_chunk_size * 1.5):
                chunk_text = " ".join(current_chunk_sentences)
                c_meta = meta.copy()
                c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_sem_{idx}"
                c_meta["semantic_score"] = float(round(sim, 3))
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
                current_chunk_sentences = [curr_sentence]
                current_len = s_len
            else:
                current_chunk_sentences.append(curr_sentence)
                current_len += s_len + 1

        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            c_meta = meta.copy()
            c_meta["chunk_id"] = f"{meta.get('passage_id', 'chunk')}_sem_{idx}"
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
