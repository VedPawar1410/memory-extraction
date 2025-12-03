"""
Memory Extraction Module

Extracts structured memory (preferences, emotional patterns, facts)
from chat history using Google Gemini.
"""

from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


class UserProfile(BaseModel):
    """Schema for extracted user profile from chat history."""
    preferences: List[str] = Field(
        description="User preferences, likes, dislikes, and choices mentioned in the conversation"
    )
    emotional_patterns: List[str] = Field(
        description="Emotional states, patterns, and behavioral tendencies observed in the conversation"
    )
    facts: List[str] = Field(
        description="Factual information about the user (name, location, occupation, relationships, etc.)"
    )


class MemoryEngine:
    """Engine for extracting structured memory from chat history."""
    
    def __init__(self, api_key: str):
        """
        Initialize the Memory Engine with Google Gemini API.
        
        Args:
            api_key: Google API key for Gemini
            
        Raises:
            ValueError: If API key is missing or invalid
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key is required and cannot be empty")
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.1  # Low temperature for more consistent extraction
            )
            self.structured_llm = self.llm.with_structured_output(UserProfile)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model: {str(e)}")
    
    def extract_from_chat(self, chat_log: str) -> UserProfile:
        """
        Extract structured memory from raw chat history.
        
        Args:
            chat_log: Raw chat conversation text
            
        Returns:
            UserProfile with extracted preferences, emotional patterns, and facts
            
        Raises:
            ValueError: If chat_log is empty or invalid
            RuntimeError: If extraction fails
        """
        if not chat_log or not chat_log.strip():
            raise ValueError("Chat log cannot be empty")
        
        # Create a detailed prompt for memory extraction
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing conversations and extracting meaningful information about users.
            
Your task is to carefully read the chat history and extract:
1. **Preferences**: What the user likes, dislikes, prefers, or chooses
2. **Emotional Patterns**: Emotional states, moods, behavioral tendencies, communication style
3. **Facts**: Concrete factual information (name, age, location, job, relationships, hobbies, etc.)

Be thorough but precise. Only extract information that is clearly stated or strongly implied.
Each item should be a clear, standalone statement."""),
            ("user", "Analyze this chat history and extract the user's profile:\n\n{chat_log}")
        ])
        
        try:
            # Invoke the structured LLM with the prompt
            chain = prompt | self.structured_llm
            result = chain.invoke({"chat_log": chat_log})
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to extract memory from chat: {str(e)}")
    
    def extract_memory(self, chat_history: str) -> UserProfile:
        """
        Legacy method name for backward compatibility.
        Alias for extract_from_chat.
        
        Args:
            chat_history: Raw chat conversation text
            
        Returns:
            UserProfile with extracted information
        """
        return self.extract_from_chat(chat_history)
