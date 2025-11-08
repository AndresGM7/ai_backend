"""Pydantic models for request/response validation."""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, description="User message")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "message": "What is the capital of France?",
                "system_prompt": "You are a helpful geography assistant."
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="Assistant response")
    message_count: int = Field(..., description="Total messages in conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "response": "The capital of France is Paris.",
                "message_count": 2
            }
        }


class Message(BaseModel):
    """Individual message in conversation history."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")


class ChatHistoryResponse(BaseModel):
    """Response model for conversation history."""
    session_id: str = Field(..., description="Session identifier")
    messages: List[Message] = Field(..., description="Conversation messages")
    message_count: int = Field(..., description="Total message count")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help you?"}
                ],
                "message_count": 2
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    redis: str
    service: str


# Example structured output model for LLM parsing
class SentimentAnalysis(BaseModel):
    """Structured output for sentiment analysis."""
    sentiment: str = Field(..., description="Positive, Negative, or Neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Explanation of the sentiment")

    class Config:
        json_schema_extra = {
            "example": {
                "sentiment": "Positive",
                "confidence": 0.95,
                "reasoning": "The text expresses happiness and satisfaction."
            }
        }

