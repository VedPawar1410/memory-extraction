"""
Memory Extraction Module

Extracts structured memory (preferences, emotional patterns, facts)
from chat history using Google Gemini.
"""

from typing import List
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI


class ExtractedMemory(BaseModel):
    """Schema for extracted memory from chat history."""
    preferences: List[str]
    emotional_patterns: List[str]
    facts: List[str]


class MemoryEngine:
    """Engine for extracting structured memory from chat history."""
    
    def __init__(self, api_key: str):
        pass
    
    def extract_memory(self, chat_history: str) -> ExtractedMemory:
        """Extract structured memory from raw chat history."""
        pass
