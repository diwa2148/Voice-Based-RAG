import logging
import httpx
from typing import List, Dict, Any
from backend.app.config import settings

logger = logging.getLogger(__name__)

class SarvamLLMService:
    """Sarvam-105B LLM Client for Grounded Context Generation via OpenAI-compatible endpoint."""
    
    def __init__(self):
        self.api_url = settings.SARVAM_LLM_ENDPOINT
        self.api_key = settings.SARVAM_API_KEY
        self.model = settings.SARVAM_LLM_MODEL
        self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _build_grounded_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        context_str = ""
        for idx, chunk in enumerate(context_chunks, start=1):
            text = chunk.get("text", "").strip()
            cid = chunk.get("chunk_id", f"chunk_{idx}")
            strat = chunk.get("chunking_strategy", "default")
            context_str += f"[Doc {idx} | Strategy: {strat} | ID: {cid}]\n{text}\n\n"

        if not context_str.strip():
            context_str = "NO CONTEXT AVAILABLE."

        prompt = f"""You are a precise, grounded RAG AI assistant. Answer the user's question STRICTLY using the provided context passages below.

STRICT INSTRUCTIONS:
1. Base your answer ONLY on the provided context passages. Do not use outside knowledge or assumptions.
2. If the context does NOT contain enough information to reliably answer the question, state: "I couldn't find enough relevant information in the provided knowledge base to answer that reliably."
3. Keep your response concise, accurate, and directly address the question.
4. Cite relevant source passage IDs where appropriate.

CONTEXT PASSAGES:
{context_str}

USER QUESTION:
{query}

GROUNDED ANSWER:"""
        return prompt

    async def generate_async(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates grounded answer using Sarvam-105B API."""
        prompt = self._build_grounded_prompt(query, context_chunks)
        
        if self.api_key:
            headers = {
                "api-subscription-key": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a grounded RAG assistant that strictly answers based on provided passages."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1024
            }
            try:
                client = self._get_client()
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=body
                )
                if response.status_code == 200:
                    res_data = response.json()
                    msg = res_data["choices"][0]["message"]
                    content = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                    return {
                        "answer": content,
                        "model_used": self.model,
                        "raw_response": res_data
                    }
                else:
                    logger.warning(f"Sarvam LLM API status {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Sarvam LLM API call error: {e}")

        # Fallback Grounded Generator for offline/demo mode
        logger.info("Using Sarvam-105B fallback grounded generator.")
        if not context_chunks:
            return {
                "answer": "I couldn't find enough relevant information in the provided knowledge base to answer that reliably.",
                "model_used": f"{self.model}-fallback"
            }

        top_passages = [c.get("text", "") for c in context_chunks[:2]]
        joined = " ".join(top_passages)
        answer = f"Based on the knowledge base: {joined[:300]}..."
        return {
            "answer": answer,
            "model_used": f"{self.model}-fallback"
        }

sarvam_llm = SarvamLLMService()
