from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Chunk(BaseModel):
    chunk_id: str
    text: str
    chunking_strategy: str
    start_char: int = 0
    end_char: int = 0
    token_count_approx: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseChunker(ABC):
    """Abstract base class for all chunking strategies."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the strategy identifier name."""
        pass

    @abstractmethod
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """Splits the input text into a list of Chunk objects."""
        pass

    def count_tokens_approx(self, text: str) -> int:
        """Approximates word/token count based on whitespace split."""
        return len(text.split())
