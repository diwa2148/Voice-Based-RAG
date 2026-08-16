import time
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional, List
from backend.app.config import settings
from backend.app.services.stt.sarvam_stt import sarvam_stt
from backend.app.services.embeddings.bge_embedder import bge_embedder
from backend.app.services.retrieval.qdrant_service import qdrant_service
from backend.app.services.retrieval.bm25_service import bm25_service
from backend.app.services.retrieval.hybrid_retriever import hybrid_retriever
from backend.app.services.reranking.bge_reranker import bge_reranker
from backend.app.services.llm.sarvam_llm import sarvam_llm
from backend.app.services.guardrails.input_guardrail import input_guardrail
from backend.app.services.guardrails.retrieval_guardrail import retrieval_guardrail
from backend.app.services.guardrails.output_guardrail import output_guardrail, CONTROLLED_REFUSAL
from backend.chunking.selector import AutoChunkingSelector
from backend.chunking.factory import get_chunker

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """Full production RAG harness coordinating all 9 pipeline stages with latency instrumentation."""
    
    async def process_pipeline_async(
        self,
        audio_bytes: Optional[bytes] = None,
        text_query: Optional[str] = None,
        strategy_override: str = "auto",
        language_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        total_start = time.perf_counter()
        
        latency_breakdown: Dict[str, float] = {}
        stage_modes: Dict[str, str] = {}
        stage_logs: List[str] = []

        # STAGE 1: SPEECH TO TEXT (STT)
        transcription = ""
        stt_start = time.perf_counter()
        if audio_bytes:
            stt_res = await sarvam_stt.transcribe_async(audio_bytes, language_code=language_filter)
            transcription = stt_res.get("transcript", "").strip() or text_query or ""
            stage_modes["stt"] = "LIVE_API" if settings.SARVAM_API_KEY else "OFFLINE_FALLBACK"
        else:
            transcription = text_query or ""
            stage_modes["stt"] = "TEXT_QUERY_DIRECT"
        latency_breakdown["stt_ms"] = float(round((time.perf_counter() - stt_start) * 1000, 2))
        stage_logs.append(f"STT completed: '{transcription}'")

        # STAGE 2: INPUT GUARDRAIL
        ig_start = time.perf_counter()
        input_passed, input_reason, sanitized_query = input_guardrail.validate(transcription)
        latency_breakdown["input_guardrail_ms"] = float(round((time.perf_counter() - ig_start) * 1000, 2))

        if not input_passed:
            total_latency = float(round((time.perf_counter() - total_start) * 1000, 2))
            return {
                "request_id": request_id,
                "query": transcription,
                "transcription": transcription,
                "answer": f"Request refused: {input_reason}",
                "status": "refused_input_guardrail",
                "chunking_strategy_used": "none",
                "retrieved_chunks": [],
                "latency_breakdown_ms": latency_breakdown,
                "total_latency_ms": total_latency,
                "stage_execution_modes": stage_modes,
                "guardrail_decisions": {"input": False, "retrieval": None, "output": None}
            }

        # Auto strategy resolution / inspection
        chunker_inst = get_chunker(strategy_override, sanitized_query, {"language": language_filter})
        selected_strategy = chunker_inst.name

        # STAGE 3 & 4: PARALLEL QUERY EMBEDDING & BM25 LEXICAL RETRIEVAL
        emb_start = time.perf_counter()
        query_vector_task = asyncio.create_task(bge_embedder.get_embedding_async(sanitized_query))
        
        bm25_start = time.perf_counter()
        bm25_candidates = bm25_service.search(sanitized_query, top_k=8)
        latency_breakdown["bm25_ms"] = float(round((time.perf_counter() - bm25_start) * 1000, 2))
        stage_modes["bm25"] = "LOCAL_INDEX"

        query_vector = await query_vector_task
        stage_modes["query_embedding"] = "LIVE_API" if settings.HF_TOKEN else "OFFLINE_FALLBACK"
        latency_breakdown["query_embedding_ms"] = float(round((time.perf_counter() - emb_start) * 1000, 2))

        # STAGE 5: DENSE VECTOR RETRIEVAL
        dense_start = time.perf_counter()
        dense_candidates = qdrant_service.search_dense(
            query_vector=query_vector,
            top_k=8,
            language_filter=language_filter,
            strategy_filter=None if strategy_override == "auto" else strategy_override
        )
        stage_modes["dense_retrieval"] = "QDRANT_CLOUD" if settings.QDRANT_URL else "QDRANT_LOCAL"
        latency_breakdown["dense_retrieval_ms"] = float(round((time.perf_counter() - dense_start) * 1000, 2))

        # STAGE 6: HYBRID SCORE FUSION (RRF)
        fusion_start = time.perf_counter()
        candidates = hybrid_retriever.fuse_results(
            dense_results=dense_candidates,
            bm25_results=bm25_candidates,
            top_k=8
        )
        stage_modes["hybrid_fusion"] = "RRF_FUSION"
        latency_breakdown["hybrid_fusion_ms"] = float(round((time.perf_counter() - fusion_start) * 1000, 2))

        # STAGE 7: RETRIEVAL GUARDRAIL & ADAPTIVE CONDITIONAL RERANKING
        rg_start = time.perf_counter()
        retrieval_passed, retrieval_reason, valid_candidates = retrieval_guardrail.validate(sanitized_query, candidates)
        latency_breakdown["retrieval_guardrail_ms"] = float(round((time.perf_counter() - rg_start) * 1000, 2))

        if not retrieval_passed or not valid_candidates:
            total_latency = float(round((time.perf_counter() - total_start) * 1000, 2))
            return {
                "request_id": request_id,
                "query": sanitized_query,
                "transcription": transcription,
                "answer": CONTROLLED_REFUSAL,
                "status": "refused_insufficient_context",
                "chunking_strategy_used": selected_strategy,
                "retrieved_chunks": [],
                "latency_breakdown_ms": latency_breakdown,
                "total_latency_ms": total_latency,
                "stage_execution_modes": stage_modes,
                "guardrail_decisions": {"input": True, "retrieval": False, "output": None}
            }

        rerank_start = time.perf_counter()
        top_score = valid_candidates[0].get("score", 0.0) if valid_candidates else 0.0
        
        # Adaptive Conditional Reranking: Bypass CrossEncoder call if top RRF score is exceptionally strong (>= 0.050)
        if top_score >= 0.050:
            top_context_chunks = valid_candidates[:3]
            stage_modes["reranking"] = "CONDITIONAL_BYPASS_HIGH_CONFIDENCE"
            latency_breakdown["reranking_ms"] = 0.0
        else:
            top_context_chunks = await bge_reranker.rerank_async(
                query=sanitized_query,
                candidates=valid_candidates[:8],
                top_k=3
            )
            stage_modes["reranking"] = "LIVE_API" if settings.HF_TOKEN else "OFFLINE_FALLBACK"
            latency_breakdown["reranking_ms"] = float(round((time.perf_counter() - rerank_start) * 1000, 2))

        # STAGE 8: LLM GROUNDED GENERATION (Sarvam-105B) - Context Pruned to Top 3 Chunks
        llm_start = time.perf_counter()
        llm_res = await sarvam_llm.generate_async(sanitized_query, top_context_chunks)
        raw_answer = llm_res.get("answer", "")
        stage_modes["llm_generation"] = "LIVE_API" if settings.SARVAM_API_KEY else "OFFLINE_FALLBACK"
        latency_breakdown["llm_generation_ms"] = float(round((time.perf_counter() - llm_start) * 1000, 2))

        # STAGE 9: OUTPUT / GROUNDING GUARDRAIL
        og_start = time.perf_counter()
        output_passed, final_answer, hallucinated = output_guardrail.validate(
            sanitized_query, raw_answer, top_context_chunks
        )
        latency_breakdown["output_guardrail_ms"] = float(round((time.perf_counter() - og_start) * 1000, 2))

        total_latency = float(round((time.perf_counter() - total_start) * 1000, 2))

        return {
            "request_id": request_id,
            "query": sanitized_query,
            "transcription": transcription,
            "answer": final_answer,
            "status": "success" if output_passed else "hallucination_refused",
            "chunking_strategy_used": selected_strategy,
            "retrieved_chunks": top_context_chunks,
            "latency_breakdown_ms": latency_breakdown,
            "total_latency_ms": total_latency,
            "stage_execution_modes": stage_modes,
            "guardrail_decisions": {
                "input": True,
                "retrieval": True,
                "output": output_passed
            }
        }

pipeline_orchestrator = PipelineOrchestrator()
