"""
Personality Engine Module

Rewrites AI responses based on extracted personas and memory context.
"""

from typing import Optional
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from memory_engine import UserProfile


class PersonalityEngine:
    """Engine for rewriting responses based on persona and memory context."""
    
    def __init__(self, user_profile: UserProfile, api_key: str):
        """
        Initialize the Personality Engine with user profile and Google Gemini API.
        
        Args:
            user_profile: UserProfile object containing user's facts, preferences, and emotional patterns
            api_key: Google API key for Gemini
            
        Raises:
            ValueError: If API key is missing or invalid
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key is required and cannot be empty")
        
        self.user_profile = user_profile
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.7  # Higher temperature for creative writing
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model: {str(e)}")
    
    def rewrite_reply(self, original_text: str, persona: str) -> str:
        """
        Rewrite a response using the specified persona and user profile context.
        
        Args:
            original_text: The original text/response to rewrite
            persona: The persona style to apply (e.g., "friendly", "professional", "casual")
            
        Returns:
            Rewritten text that matches the persona and incorporates user context
            
        Raises:
            ValueError: If original_text or persona is empty
            RuntimeError: If rewriting fails
        """
        if not original_text or not original_text.strip():
            raise ValueError("Original text cannot be empty")
        if not persona or not persona.strip():
            raise ValueError("Persona cannot be empty")
        
        # Format user profile information
        facts_text = "\n".join(f"- {fact}" for fact in self.user_profile.facts) if self.user_profile.facts else "None provided"
        preferences_text = "\n".join(f"- {pref}" for pref in self.user_profile.preferences) if self.user_profile.preferences else "None provided"
        emotional_patterns_text = "\n".join(f"- {pattern}" for pattern in self.user_profile.emotional_patterns) if self.user_profile.emotional_patterns else "None provided"
        
        # Create prompt template with user context injected
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at rewriting text to match specific personas while incorporating personalized context.

**User Context:**

Facts about the user:
{facts}

User preferences:
{preferences}

Emotional patterns and communication style:
{emotional_patterns}

**Your Task:**
Rewrite the provided text to match the "{persona}" persona while naturally incorporating relevant details from the user context above. The rewritten text should:
1. Match the tone and style of the {persona} persona
2. Feel personalized and contextually aware of the user
3. Maintain the core message and intent of the original text
4. Sound natural and conversational, not forced

Be creative but authentic. Only incorporate user context when it feels natural and relevant."""),
            ("user", "Original text to rewrite:\n\n{original_text}")
        ])
        
        try:
            # Invoke the LLM with the prompt
            chain = prompt | self.llm
            result = chain.invoke({
                "facts": facts_text,
                "preferences": preferences_text,
                "emotional_patterns": emotional_patterns_text,
                "persona": persona,
                "original_text": original_text
            })
            
            # Extract the content from the AIMessage response
            return result.content
        except Exception as e:
            raise RuntimeError(f"Failed to rewrite text: {str(e)}")
    
    def rewrite_response(
        self,
        original_response: str,
        persona: str,
        memory: Optional[UserProfile] = None
    ) -> str:
        """
        Legacy method for backward compatibility.
        Alias for rewrite_reply.
        
        Args:
            original_response: The original text/response to rewrite
            persona: The persona style to apply
            memory: Optional UserProfile to override the instance profile
            
        Returns:
            Rewritten text that matches the persona
        """
        # If a different memory/profile is provided, temporarily use it
        if memory is not None:
            original_profile = self.user_profile
            self.user_profile = memory
            try:
                return self.rewrite_reply(original_response, persona)
            finally:
                self.user_profile = original_profile
        else:
            return self.rewrite_reply(original_response, persona)
