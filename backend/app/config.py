import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Sarvam AI API Configuration
    SARVAM_API_KEY: str = ""
    SARVAM_STT_ENDPOINT: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_LLM_ENDPOINT: str = "https://api.sarvam.ai/v1/chat/completions"
    SARVAM_STT_MODEL: str = "saaras:v3"
    SARVAM_LLM_MODEL: str = "sarvam-105b"

    # Hugging Face / Hosted Inference API
    HF_TOKEN: str = ""
    EMBEDDING_API_URL: str = "https://router.huggingface.co/hf-inference/models/BAAI/bge-large-en-v1.5"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024

    RERANKER_API_URL: str = "https://router.huggingface.co/hf-inference/models/BAAI/bge-reranker-v2-m3"
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-v2-m3"

    # Qdrant Database Configuration
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "msmarco_xi_chunks"
    QDRANT_STORAGE_DIR: str = "./qdrant_data"

    # Retrieval & Pipeline Parameters
    DEFAULT_CHUNKING_STRATEGY: str = "auto"
    TOP_K_RETRIEVAL: int = 20
    TOP_K_RERANK: int = 5
    MIN_RETRIEVAL_SCORE: float = 0.015
    ENABLE_RERANKER: bool = True

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
