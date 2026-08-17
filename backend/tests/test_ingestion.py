import pytest
import asyncio
from backend.ingestion.ingest_msmarco import extract_passages_from_item, ingest_dataset

def test_extract_passages_from_item_translated():
    item = {
        "query_id": 404,
        "source_lang": "en",
        "target_lang": "hi",
        "query_type": "description",
        "passages": {
            "is_selected": [0, 1],
            "English_passages": ["English passage text with enough length to pass length check"],
            "Translated_passages": ["हिन्दी पैसेज टेक्स्ट जिसमें बीस से अधिक अक्षर हैं"]
        }
    }
    extracted = extract_passages_from_item(item)
    assert len(extracted) == 1
    assert extracted[0]["query_id"] == "404"
    assert extracted[0]["source_lang"] == "en"
    assert extracted[0]["target_lang"] == "hi"
    assert extracted[0]["query_type"] == "description"
    assert extracted[0]["language"] == "hi"
    assert extracted[0]["source"] == "HuggingFace-MSMARCO-XI"
    assert extracted[0]["text"] == "हिन्दी पैसेज टेक्स्ट जिसमें बीस से अधिक अक्षर हैं"

def test_extract_passages_from_item_english_fallback():
    item = {
        "query_id": "505",
        "source_lang": "en",
        "target_lang": "hi",
        "query_type": "numeric",
        "passages": {
            "is_selected": [1],
            "English_passages": ["English fallback passage text with enough length"],
            "Translated_passages": []
        }
    }
    extracted = extract_passages_from_item(item)
    assert len(extracted) == 1
    assert extracted[0]["query_id"] == "505"
    assert extracted[0]["language"] == "en"
    assert extracted[0]["text"] == "English fallback passage text with enough length"

def test_extract_passages_from_item_list_structure():
    item = {
        "query_id": "606",
        "source_lang": "ta",
        "target_lang": "ta",
        "query_type": "entity",
        "passages": [
            {
                "passage_id": "p1",
                "passage_text": "Tamil passage text item with enough characters for chunking"
            }
        ]
    }
    extracted = extract_passages_from_item(item)
    assert len(extracted) == 1
    assert extracted[0]["passage_id"] == "p1"
    assert extracted[0]["source_lang"] == "ta"
    assert extracted[0]["target_lang"] == "ta"

def test_ingest_dataset_seed_only():
    result = asyncio.run(ingest_dataset(seed_only=True))
    assert result["passages_processed"] == 10
    assert result["chunks_indexed"] > 0
    assert result["qdrant_points"] > 0
