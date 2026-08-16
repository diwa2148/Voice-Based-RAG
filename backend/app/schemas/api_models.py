from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class STTResponse(BaseModel):
    transcript: str
    language_code: Optional[str] = "en-IN"
    latency_ms: float = 0.0

class QueryRequest(BaseModel):
    query: Optional[str] = Field(None, description="Text query if not providing voice input")
    strategy_override: Optional[str] = Field("auto", description="Strategy override or 'auto'")
    language_filter: Optional[str] = Field(None, description="Language code filter e.g. hi, bn, ta, te, en")

class ChunkResponse(BaseModel):
    chunk_id: str
    text: str
    score: float
    chunking_strategy: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QueryResponse(BaseModel):
    request_id: str
    query: str
    transcription: str
    answer: str
    status: str
    chunking_strategy_used: str
    retrieved_chunks: List[ChunkResponse]
    latency_breakdown_ms: Dict[str, float]
    total_latency_ms: float
    guardrail_decisions: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    qdrant_healthy: bool
    embedding_service: str
    reranker_service: str
    stt_model: str
    llm_model: str

class BenchmarkResponse(BaseModel):
    timestamp: str
    total_queries_tested: int
    bottleneck_stage: str
    bottleneck_p50_ms: float
    percentiles: Dict[str, Dict[str, float]]
    query_results: List[Dict[str, Any]]
