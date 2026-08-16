import time
import logging
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.schemas.api_models import (
    STTResponse, QueryRequest, QueryResponse, HealthResponse, BenchmarkResponse
)
from backend.app.services.stt.sarvam_stt import sarvam_stt
from backend.app.services.retrieval.qdrant_service import qdrant_service
from backend.app.services.orchestration.pipeline_orchestrator import pipeline_orchestrator
from backend.benchmarking.run_benchmark import run_benchmark_suite

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("main")

app = FastAPI(
    title="HH Goa 2026 Voice-Enabled RAG API",
    description="Production-quality Voice RAG pipeline with Sarvam STT, BGE-M3, Qdrant, BM25, BGE Reranker, Sarvam-105B LLM, 7 Chunking Strategies, 3 Guardrail Levels, and Latency Benchmarking.",
    version="1.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    q_ok = qdrant_service.is_healthy()
    return HealthResponse(
        status="healthy" if q_ok else "degraded",
        qdrant_healthy=q_ok,
        embedding_service=settings.EMBEDDING_MODEL_NAME,
        reranker_service=settings.RERANKER_MODEL_NAME,
        stt_model=settings.SARVAM_STT_MODEL,
        llm_model=settings.SARVAM_LLM_MODEL
    )

@app.post("/api/stt", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language_code: Optional[str] = Form(None)
):
    start_t = time.perf_counter()
    try:
        audio_bytes = await file.read()
        res = await sarvam_stt.transcribe_async(
            audio_bytes,
            filename=file.filename or "recording.wav",
            language_code=language_code
        )
        elapsed_ms = float(round((time.perf_counter() - start_t) * 1000, 2))
        return STTResponse(
            transcript=res.get("transcript", ""),
            language_code=res.get("language_code", "en-IN"),
            latency_ms=elapsed_ms
        )
    except Exception as e:
        logger.error(f"Error processing STT upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse)
async def execute_query(
    audio_file: Optional[UploadFile] = File(None),
    text_query: Optional[str] = Form(None),
    strategy_override: Optional[str] = Form("auto"),
    language_filter: Optional[str] = Form(None)
):
    try:
        audio_bytes = None
        if audio_file:
            audio_bytes = await audio_file.read()

        result = await pipeline_orchestrator.process_pipeline_async(
            audio_bytes=audio_bytes,
            text_query=text_query,
            strategy_override=strategy_override or "auto",
            language_filter=language_filter
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Pipeline orchestration error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

@app.post("/api/benchmark", response_model=BenchmarkResponse)
async def run_benchmark():
    try:
        report = await run_benchmark_suite()
        return BenchmarkResponse(**report)
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
