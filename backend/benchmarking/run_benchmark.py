import os
import sys
import time
import json
import logging
import asyncio
import numpy as np
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.services.orchestration.pipeline_orchestrator import pipeline_orchestrator
from backend.app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_benchmark")

BENCHMARK_QUERIES = [
    {"query": "What languages are included in the MS MARCO XI dataset?", "lang": "en"},
    {"query": "Retrieval Augmented Generation architecture and vector database details", "lang": "en"},
    {"query": "Sarvam Saaras v3 speech to text model features", "lang": "en"},
    {"query": "BAAI BGE-M3 dense and sparse embedding dimensions", "lang": "en"},
    {"query": "Qdrant vector search and payload filtering capabilities", "lang": "en"},
    {"query": "এমএস মার্কো একাদশ ডেটাসেটের বিবরণ কি?", "lang": "bn"},
    {"query": "हिंदी में एमएस मार्को dataset की जानकारी दीजिए", "lang": "hi"},
    {"query": "தமிழ் மொழியில் பெறப்பட்ட వివరங்கள் என்ன?", "lang": "ta"},
    {"query": "తెలుగు సేకరణ ఆధారంగా వివరాలు వివరించండి", "lang": "te"},
    {"query": "How does BM25 keyword search combine with Qdrant vector search?", "lang": "en"},
    {"query": "Explain Sarvam-105B LLM prompt construction and grounding instructions", "lang": "en"},
    {"query": "What are the 3 levels of guardrails in this RAG system?", "lang": "en"},
    {"query": "Invalid quantum computing cryptography supercomputer query test", "lang": "en"},
    {"query": "Fixed-size vs Sentence vs Semantic chunking strategy comparison", "lang": "en"},
    {"query": "Full process latency target under 200 ms optimization", "lang": "en"}
]

def calculate_percentiles(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"p50": 0.0, "p70": 0.0, "p100": 0.0}
    arr = np.array(values)
    return {
        "p50": float(round(np.percentile(arr, 50), 2)),
        "p70": float(round(np.percentile(arr, 70), 2)),
        "p100": float(round(np.percentile(arr, 100), 2))
    }

async def run_benchmark_suite(num_runs: int = 1) -> Dict[str, Any]:
    logger.info(f"Starting RAG Benchmark Suite over {len(BENCHMARK_QUERIES)} test queries...")
    
    stage_metrics: Dict[str, List[float]] = {
        "stt_ms": [],
        "input_guardrail_ms": [],
        "query_embedding_ms": [],
        "bm25_ms": [],
        "dense_retrieval_ms": [],
        "hybrid_fusion_ms": [],
        "retrieval_guardrail_ms": [],
        "reranking_ms": [],
        "llm_generation_ms": [],
        "output_guardrail_ms": [],
        "total_latency_ms": []
    }

    results_detail = []
    last_execution_modes = {}

    for idx, q_item in enumerate(BENCHMARK_QUERIES, start=1):
        query_text = q_item["query"]
        lang = q_item["lang"]
        logger.info(f"[{idx}/{len(BENCHMARK_QUERIES)}] Executing query: '{query_text[:50]}...'")

        res = await pipeline_orchestrator.process_pipeline_async(
            text_query=query_text,
            language_filter=lang,
            strategy_override="auto"
        )

        b_down = res.get("latency_breakdown_ms", {})
        total_lat = res.get("total_latency_ms", 0.0)
        last_execution_modes = res.get("stage_execution_modes", {})

        for stage, val in b_down.items():
            if stage in stage_metrics:
                stage_metrics[stage].append(val)
        stage_metrics["total_latency_ms"].append(total_lat)

        results_detail.append({
            "query": query_text,
            "status": res.get("status"),
            "strategy_used": res.get("chunking_strategy_used"),
            "total_latency_ms": total_lat,
            "breakdown_ms": b_down
        })

    # Compute P50, P70, P100 for every stage
    stage_percentiles: Dict[str, Dict[str, float]] = {}
    bottleneck_stage = "none"
    max_p50 = -1.0

    for stage, vals in stage_metrics.items():
        pcts = calculate_percentiles(vals)
        stage_percentiles[stage] = pcts
        if stage != "total_latency_ms" and pcts["p50"] > max_p50:
            max_p50 = pcts["p50"]
            bottleneck_stage = stage

    has_live_credentials = bool(settings.SARVAM_API_KEY and settings.HF_TOKEN)

    summary_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries_tested": len(BENCHMARK_QUERIES),
        "execution_environment": "LIVE_HOSTED_APIS" if has_live_credentials else "LIGHTWEIGHT_OFFLINE_FALLBACK",
        "stage_execution_modes": last_execution_modes,
        "bottleneck_stage": bottleneck_stage,
        "bottleneck_p50_ms": max_p50,
        "percentiles": stage_percentiles,
        "query_results": results_detail
    }

    logger.info("=== RAG BENCHMARK SUMMARY (P50 / P70 / P100) ===")
    logger.info(f"Execution Mode: {summary_report['execution_environment']}")
    logger.info(f"Identified Bottleneck Stage: {bottleneck_stage} (P50: {max_p50} ms)")
    for stage, pcts in stage_percentiles.items():
        logger.info(f"Stage '{stage:25s}' -> P50: {pcts['p50']:7.2f} ms | P70: {pcts['p70']:7.2f} ms | P100: {pcts['p100']:7.2f} ms")

    return summary_report

if __name__ == "__main__":
    report = asyncio.run(run_benchmark_suite())
    with open("benchmark_report.json", "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Saved full report to benchmark_report.json")
