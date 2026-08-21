import os
import sys
import logging
import asyncio
import argparse
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.config import settings
from backend.chunking import chunk_text
from backend.app.services.embeddings.bge_embedder import bge_embedder
from backend.app.services.retrieval.qdrant_service import qdrant_service
from backend.app.services.retrieval.bm25_service import bm25_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_msmarco")

# Expanded high quality seed MSMARCO-XI dataset passages
SEED_PASSAGES = [
    {
        "query_id": "q_101",
        "passage_id": "p_101",
        "language": "hi",
        "source": "MSMARCO-XI-Hindi",
        "text": "MS MARCO-XI is a multilingual retrieval dataset created for benchmarking information retrieval in Indian languages including Hindi, Bengali, Tamil, Telugu, and English."
    },
    {
        "query_id": "q_102",
        "passage_id": "p_102",
        "language": "en",
        "source": "MSMARCO-XI-English",
        "text": "Retrieval-Augmented Generation (RAG) combines semantic retrieval with large language models to produce grounded answers. By indexing passages into Qdrant vector database and BM25 index, hybrid retrieval delivers high accuracy."
    },
    {
        "query_id": "q_103",
        "passage_id": "p_103",
        "language": "bn",
        "source": "MSMARCO-XI-Bengali",
        "text": "Sarvam Saaras v3 is a state-of-the-art Speech-to-Text model designed specifically for Indian accents and multilingual speech transcription."
    },
    {
        "query_id": "q_104",
        "passage_id": "p_104",
        "language": "ta",
        "source": "MSMARCO-XI-Tamil",
        "text": "BAAI BGE-M3 is a powerful dense embedding model supporting dense retrieval, sparse retrieval, and multi-vector retrieval across 100+ languages."
    },
    {
        "query_id": "q_105",
        "passage_id": "p_105",
        "language": "te",
        "source": "MSMARCO-XI-Telugu",
        "text": "Qdrant is a high-performance vector database with payload filtering and fast ANN search designed for production RAG pipelines."
    },
    {
        "query_id": "q_106",
        "passage_id": "p_106",
        "language": "en",
        "source": "MSMARCO-XI-English",
        "text": "HH Goa 2026 Shortlisting Task 2 requires building a production voice-enabled RAG system with Sarvam STT, BGE-M3, Qdrant, BM25, Sarvam-105B LLM, and 3 levels of guardrails."
    },
    {
        "query_id": "q_107",
        "passage_id": "p_107",
        "language": "en",
        "source": "MSMARCO-XI-English",
        "text": "The 7 chunking strategies implemented in this system are Fixed-size, Fixed-size with overlap, Sentence-based, Paragraph-based, Recursive, Semantic, and Metadata-aware chunking."
    },
    {
        "query_id": "q_108",
        "passage_id": "p_108",
        "language": "hi",
        "source": "MSMARCO-XI-Hindi",
        "text": "एमएस मार्को dataset का मुख्य उद्देश्य भारतीय भाषाओं के लिए सटीक इनफार्मेशन रिट्रीवल और सर्च एल्गोरिदम का मूल्यांकन करना है।"
    },
    {
        "query_id": "q_109",
        "passage_id": "p_109",
        "language": "bn",
        "source": "MSMARCO-XI-Bengali",
        "text": "এমএস মার্কো একাদশ ডেটাসেটে বাংলা ভাষার জন্য তথ্য পুনরুদ্ধারের উদ্দেশ্যে বিশেষ প্যাসেজ এবং প্রশ্ন অন্তর্ভুক্ত করা হয়েছে।"
    },
    {
        "query_id": "q_110",
        "passage_id": "p_110",
        "language": "en",
        "source": "MSMARCO-XI-English",
        "text": "The 3 levels of guardrails consist of Input Guardrail for query safety, Retrieval Guardrail for context score thresholding, and Output Guardrail for hallucination prevention."
    }
]


def extract_passages_from_item(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Safely extracts passages and metadata from a HuggingFace MSMARCO-XI dataset item.
    Dataset schema features:
      source_lang, target_lang, meta, Answer, query_id, query_type, passages, Eng_Query, Eng_Answer, query
    passages field structure:
      dict with 'Translated_passages', 'English_passages', 'is_selected', 'passage_text', 'text'
      or a list of passage objects/strings.
    """
    query_id = str(item.get("query_id", "0"))
    source_lang = str(item.get("source_lang", "")) if item.get("source_lang") is not None else ""
    target_lang = str(item.get("target_lang", "")) if item.get("target_lang") is not None else ""
    query_type = str(item.get("query_type", "")) if item.get("query_type") is not None else ""
    default_lang = target_lang or source_lang or "hi"

    passages_raw = item.get("passages")
    extracted = []

    if isinstance(passages_raw, dict):
        translated_list = passages_raw.get("Translated_passages") or []
        english_list = passages_raw.get("English_passages") or []
        passage_text_list = passages_raw.get("passage_text") or passages_raw.get("text") or []

        target_texts = []
        chosen_lang = default_lang

        if isinstance(translated_list, list) and any(isinstance(t, str) and t.strip() for t in translated_list):
            target_texts = translated_list
            chosen_lang = default_lang
        elif isinstance(english_list, list) and any(isinstance(t, str) and t.strip() for t in english_list):
            target_texts = english_list
            chosen_lang = "en"
        elif isinstance(passage_text_list, list) and any(isinstance(t, str) and t.strip() for t in passage_text_list):
            target_texts = passage_text_list
            chosen_lang = default_lang

        for idx, text in enumerate(target_texts):
            if isinstance(text, str) and len(text.strip()) > 20:
                p_id = f"hf_p_{query_id}_{idx}"
                extracted.append({
                    "query_id": query_id,
                    "passage_id": p_id,
                    "language": chosen_lang,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "query_type": query_type,
                    "source": "HuggingFace-MSMARCO-XI",
                    "text": text.strip()
                })

    elif isinstance(passages_raw, list):
        for idx, p in enumerate(passages_raw):
            if isinstance(p, dict):
                text = p.get("passage_text") or p.get("text") or p.get("Translated_passage") or p.get("English_passage") or ""
                p_id = str(p.get("passage_id") or p.get("id") or f"hf_p_{query_id}_{idx}")
                p_lang = str(p.get("language") or default_lang)
            elif isinstance(p, str):
                text = p
                p_id = f"hf_p_{query_id}_{idx}"
                p_lang = default_lang
            else:
                text = ""
                p_id = f"hf_p_{query_id}_{idx}"
                p_lang = default_lang

            if isinstance(text, str) and len(text.strip()) > 20:
                extracted.append({
                    "query_id": query_id,
                    "passage_id": p_id,
                    "language": p_lang,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "query_type": query_type,
                    "source": "HuggingFace-MSMARCO-XI",
                    "text": text.strip()
                })

    elif isinstance(passages_raw, str) and len(passages_raw.strip()) > 20:
        extracted.append({
            "query_id": query_id,
            "passage_id": f"hf_p_{query_id}_0",
            "language": default_lang,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "query_type": query_type,
            "source": "HuggingFace-MSMARCO-XI",
            "text": passages_raw.strip()
        })

    return extracted


async def ingest_dataset(seed_only: bool = False, max_passages: int = 50):
    logger.info("Starting MSMARCO-XI Dataset Ingestion Pipeline...")
    passages_to_process = list(SEED_PASSAGES)

    if not seed_only and max_passages > 0:
        try:
            from datasets import load_dataset
            logger.info(f"Attempting HuggingFace streaming load of 'ai4bharat/MSMARCO-XI' (max_passages: {max_passages})...")
            dataset = None
            try:
                dataset = load_dataset("ai4bharat/MSMARCO-XI", split="train", streaming=True)
            except Exception as se:
                logger.info(f"Streaming load failed ({se}), attempting non-streaming load...")
                dataset = load_dataset("ai4bharat/MSMARCO-XI", split="train", streaming=False)

            hf_count = 0
            for item in dataset:
                if hf_count >= max_passages:
                    break
                extracted_passages = extract_passages_from_item(item)
                for p in extracted_passages:
                    passages_to_process.append(p)
                    hf_count += 1
                    if hf_count >= max_passages:
                        break
            logger.info(f"Streamed {hf_count} passages from Hugging Face.")
        except Exception as e:
            logger.warning(f"HuggingFace dataset stream fallback triggered ({e}). Using seed passages.")

    logger.info(f"Processing total of {len(passages_to_process)} passages through Chunking Strategies...")

    all_chunks = []

    STRATEGIES = [
        "fixed",
        "fixed_overlap",
        "sentence",
        "paragraph",
        "recursive",
        "semantic",
        "metadata_aware"
    ]

    for item in passages_to_process:
        meta = {
            "query_id": item.get("query_id"),
            "passage_id": item.get("passage_id"),
            "language": item.get("language"),
            "source_lang": item.get("source_lang"),
            "target_lang": item.get("target_lang"),
            "query_type": item.get("query_type"),
            "source": item.get("source")
        }

        meta = {k: v for k, v in meta.items() if v is not None}

        for strategy in STRATEGIES:
            chunks = chunk_text(
                item["text"],
                strategy_name=strategy,
                metadata=meta
            )
            all_chunks.extend(chunks)

    logger.info(f"Generated {len(all_chunks)} chunks. Generating embeddings via BGE-M3...")

    texts = [c.text for c in all_chunks]
    embeddings = await bge_embedder.get_embeddings_batch_async(texts)

    logger.info("Upserting vectors into Qdrant collection...")
    qdrant_service.ensure_collection()
    upserted_count = qdrant_service.upsert_chunks(all_chunks, embeddings)
    logger.info(f"Upserted {upserted_count} vector points into Qdrant.")

    logger.info("Building BM25 keyword index...")
    bm25_service.build_index(all_chunks)
    logger.info("BM25 index built and saved to disk.")

    logger.info("Dataset Ingestion Pipeline Finished Successfully!")
    return {
        "passages_processed": len(passages_to_process),
        "chunks_indexed": len(all_chunks),
        "qdrant_points": upserted_count
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest MSMARCO-XI dataset into Qdrant & BM25 index")
    parser.add_argument("--seed-only", action="store_true", help="Use seed passages only for fast ingestion")
    parser.add_argument("--max-passages", type=int, default=50, help="Maximum number of Hugging Face passages to ingest (default: 50)")
    args = parser.parse_args()
    asyncio.run(ingest_dataset(seed_only=args.seed_only, max_passages=args.max_passages))

