"""
Chat session model for MongoDB.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

from .user import PyObjectId


class SessionMode(str, Enum):
    """Session mode enumeration."""
    LAWS_PUBLIC = "laws_public"
    LAWS_INTERNAL = "laws_internal"


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    CLOSED = "closed"


class Session(BaseModel):
    """Chat session model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to user")
    mode: SessionMode = Field(..., description="Session mode (public/internal laws)")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Session status")
    title: Optional[str] = Field(None, description="Session title (auto-generated from first message)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "mode": "laws_public",
                "status": "active",
                "title": "Consultation about labor law"
            }
        }
    
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE
    
    def close_session(self) -> None:
        """Close the session."""
        self.status = SessionStatus.CLOSED
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class SessionInDB(Session):
    """Session model with additional database fields."""
    
    message_count: int = Field(default=0)
    total_tokens: int = Field(default=0)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
