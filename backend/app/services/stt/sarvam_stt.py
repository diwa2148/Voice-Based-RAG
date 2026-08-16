import os
import logging
import httpx
from typing import Dict, Any, Optional
from backend.app.config import settings

logger = logging.getLogger(__name__)

class SarvamSTTService:
    """Service for Sarvam AI Saaras v3 Speech-To-Text API with fallback driver."""
    
    def __init__(self):
        self.api_url = settings.SARVAM_STT_ENDPOINT
        self.api_key = settings.SARVAM_API_KEY
        self.model = settings.SARVAM_STT_MODEL

    async def transcribe_async(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribes raw audio bytes using Sarvam Saaras v3 API."""
        if not audio_bytes:
            return {"transcript": "", "language_code": "unknown", "error": "Empty audio data"}

        if self.api_key:
            headers = {"api-subscription-key": self.api_key}
            files = {"file": (filename, audio_bytes, "audio/wav")}
            data = {
                "model": self.model,
                "mode": "transcribe"
            }
            if language_code:
                lang_tag = language_code
                if len(language_code) == 2:
                    lang_map = {"en": "en-IN", "hi": "hi-IN", "bn": "bn-IN", "ta": "ta-IN", "te": "te-IN", "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "gu": "gu-IN", "pa": "pa-IN"}
                    lang_tag = lang_map.get(language_code.lower(), f"{language_code}-IN")
                data["language_code"] = lang_tag

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        files=files,
                        data=data
                    )
                    if response.status_code == 200:
                        res_json = response.json()
                        transcript = res_json.get("transcript", res_json.get("text", "")).strip()
                        lang = res_json.get("language_code", language_code or "hi-IN")
                        return {
                            "transcript": transcript,
                            "language_code": lang,
                            "raw_response": res_json
                        }
                    else:
                        logger.warning(f"Sarvam STT API returned status {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Error calling Sarvam STT API: {e}")

        # Fallback Mock STT Driver for offline / demo mode
        logger.info("Using Sarvam STT mock fallback driver.")
        # If input bytes contain text payload or default query
        try:
            decoded_text = audio_bytes.decode("utf-8", errors="ignore").strip()
            if len(decoded_text) > 3 and not any(ord(c) < 32 for c in decoded_text[:20]):
                return {
                    "transcript": decoded_text,
                    "language_code": language_code or "en-IN",
                    "note": "Text passed to STT driver"
                }
        except Exception:
            pass

        return {
            "transcript": "What languages and passages are included in the MS MARCO XI dataset?",
            "language_code": "en-IN",
            "note": "Default mock transcription (Sarvam API Key required for live STT)"
        }

sarvam_stt = SarvamSTTService()
