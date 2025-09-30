"""
Admin log model for MongoDB.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

from .user import PyObjectId


class AdminAction(str, Enum):
    """Admin action enumeration."""
    CRAWL_LAWS = "crawl_laws"
    UPLOAD_LAWS = "upload_laws"
    GENERATE_REPORT = "generate_report"
    DEACTIVATE_ACCOUNT = "deactivate_account"
    ACTIVATE_ACCOUNT = "activate_account"
    QUERY_ACCOUNT = "query_account"
    DELETE_SESSION = "delete_session"
    BULK_DELETE_SESSIONS = "bulk_delete_sessions"
    SYSTEM_MAINTENANCE = "system_maintenance"
    UPDATE_SETTINGS = "update_settings"


class AdminLog(BaseModel):
    """Admin action log model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    admin_id: PyObjectId = Field(..., description="Reference to admin user")
    action: AdminAction = Field(..., description="Admin action performed")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    result: Dict[str, Any] = Field(default_factory=dict, description="Action result")
    success: bool = Field(default=True, description="Whether action succeeded")
    error_message: Optional[str] = Field(None, description="Error message if action failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "admin_id": "507f1f77bcf86cd799439011",
                "action": "crawl_laws",
                "params": {
                    "law_type": "enterprises",
                    "year": "2020"
                },
                "result": {
                    "documents_processed": 150,
                    "chunks_created": 1200,
                    "embeddings_generated": 1200
                },
                "success": True,
                "execution_time": 45.2
            }
        }
    
    def is_successful(self) -> bool:
        """Check if admin action was successful."""
        return self.success
    
    def has_error(self) -> bool:
        """Check if admin action had errors."""
        return not self.success or self.error_message is not None


class AdminLogInDB(AdminLog):
    """Admin log model with additional database fields."""
    
    # Additional tracking
    ip_address: Optional[str] = Field(None, description="Admin IP address")
    user_agent: Optional[str] = Field(None, description="Admin user agent")
    session_id: Optional[str] = Field(None, description="Admin session ID")
