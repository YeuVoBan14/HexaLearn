# For later if want to change to Claude or OpenAI

import logging
from django.conf import settings
from google import genai 
from google.genai import types
from .ai_prompts import SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-2.5-flash-lite"

def get_gemini_client():
    """Khởi tạo Gemini client từ GEMINI_API_KEY env var."""
    try:
        return genai.Client()  # ← SDK mới
    except ImportError:
        raise ImportError(
            "google-genai is not installed. "
            "Run: pip install google-genai"
        )
    
def stream_gemini_response(user_prompt: str):
    """
    Generator function — yield từng chunk text từ Gemini.
 
    Usage:
        for chunk in stream_gemini_response(system, prompt):
            yield chunk
 
    Gemini 1.5 Flash free tier limits:
        - 15 RPM (requests per minute)
        - 1 million TPM (tokens per minute)
        - 1,500 RPD (requests per day)
    Đủ dùng cho development và small production.
    """
    client = get_gemini_client()
 
    model_name = GEMINI_MODEL
 
    try:
        response = client.models.generate_content_stream(
            model=model_name,
            contents=[user_prompt],  # ← Array contents
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION),
                )
        
        for chunk in response:
            if chunk.candidates and chunk.candidates[0].content.parts:
                text = chunk.candidates[0].content.parts[0].text
                if text:
                    yield text
                    
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        yield f"\n\n[Error: {str(e)}]"
 