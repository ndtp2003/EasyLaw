"""
Chat schemas for API validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.session import SessionMode, SessionStatus
from app.models.message import MessageSender


class SessionCreate(BaseModel):
    """Create new chat session schema."""
    
    mode: SessionMode = Field(..., description="Session mode (public/internal laws)")
    title: Optional[str] = Field(None, max_length=200, description="Optional session title")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "laws_public",
                "title": "Labor law consultation"
            }
        }


class SessionResponse(BaseModel):
    """Chat session response schema."""
    
    id: str = Field(..., description="Session ID")
    mode: SessionMode = Field(..., description="Session mode")
    status: SessionStatus = Field(..., description="Session status")
    title: Optional[str] = Field(None, description="Session title")
    message_count: int = Field(default=0, description="Number of messages")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "mode": "laws_public",
                "status": "active",
                "title": "Labor law consultation",
                "message_count": 5,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:15:00Z"
            }
        }


class MessageCreate(BaseModel):
    """Create new message schema."""
    
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")
    session_id: str = Field(..., description="Target session ID")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "What are the requirements for establishing a company in Vietnam?",
                "session_id": "507f1f77bcf86cd799439011"
            }
        }


class MessageResponse(BaseModel):
    """Message response schema."""
    
    id: str = Field(..., description="Message ID")
    session_id: str = Field(..., description="Session ID")
    sender: MessageSender = Field(..., description="Message sender")
    content: str = Field(..., description="Message content")
    tokens: int = Field(default=0, description="Token count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "session_id": "507f1f77bcf86cd799439011",
                "sender": "assistant",
                "content": "To establish a company in Vietnam, you need to follow these steps...",
                "tokens": 45,
                "metadata": {
                    "rag_sources": ["Law on Enterprises 2020"],
                    "response_time": 1.2
                },
                "created_at": "2024-01-01T12:10:00Z"
            }
        }


class ChatHistoryResponse(BaseModel):
    """Chat history response schema."""
    
    session: SessionResponse = Field(..., description="Session information")
    messages: List[MessageResponse] = Field(..., description="Chat messages")
    total_messages: int = Field(..., description="Total message count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session": {
                    "id": "507f1f77bcf86cd799439011",
                    "mode": "laws_public",
                    "status": "active",
                    "title": "Labor law consultation",
                    "message_count": 2,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:10:00Z"
                },
                "messages": [],
                "total_messages": 2
            }
        }


class SessionsListResponse(BaseModel):
    """User sessions list response schema."""
    
    sessions: List[SessionResponse] = Field(..., description="User sessions")
    total_sessions: int = Field(..., description="Total session count")
    active_sessions: int = Field(..., description="Active session count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [],
                "total_sessions": 5,
                "active_sessions": 2
            }
        }


class StreamingResponse(BaseModel):
    """Streaming chat response schema."""
    
    type: str = Field(..., description="Response type: 'token', 'complete', 'error'")
    content: Optional[str] = Field(None, description="Response content")
    message_id: Optional[str] = Field(None, description="Message ID (for complete responses)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "token",
                "content": "To establish",
                "metadata": {}
            }
        }
