"""
Chat message model for MongoDB.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

from .user import PyObjectId


class MessageSender(str, Enum):
    """Message sender enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Chat message model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: PyObjectId = Field(..., description="Reference to chat session")
    sender: MessageSender = Field(..., description="Message sender")
    content: str = Field(..., description="Message content")
    tokens: int = Field(default=0, description="Token count for this message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "session_id": "507f1f77bcf86cd799439011",
                "sender": "user",
                "content": "What are the requirements for establishing a company in Vietnam?",
                "tokens": 12,
                "metadata": {
                    "rag_sources": ["Law on Enterprises 2020"],
                    "response_time": 1.2
                }
            }
        }
    
    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.sender == MessageSender.USER
    
    def is_from_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.sender == MessageSender.ASSISTANT
    
    def is_system_message(self) -> bool:
        """Check if message is system message."""
        return self.sender == MessageSender.SYSTEM


class MessageInDB(Message):
    """Message model with additional database fields."""
    
    # RAG-specific fields
    rag_sources: Optional[list] = Field(default_factory=list, description="RAG source documents")
    embedding_id: Optional[str] = Field(None, description="Reference to vector embedding")
    similarity_scores: Optional[Dict[str, float]] = Field(default_factory=dict)
    
    # Performance metrics
    response_time: Optional[float] = Field(None, description="Response generation time in seconds")
    ai_model_used: Optional[str] = Field(None, description="AI model used for generation")
