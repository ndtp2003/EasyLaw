"""
Admin schemas for API validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.admin_log import AdminAction


class CrawlLawsRequest(BaseModel):
    """Crawl laws request schema."""
    
    law_types: List[str] = Field(
        default=["enterprises", "labor"], 
        description="Types of laws to crawl"
    )
    force_update: bool = Field(default=False, description="Force re-crawl existing laws")
    
    @validator('law_types')
    def validate_law_types(cls, v):
        valid_types = ["enterprises", "labor", "all"]
        for law_type in v:
            if law_type not in valid_types:
                raise ValueError(f'Invalid law type: {law_type}. Valid types: {valid_types}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "law_types": ["enterprises", "labor"],
                "force_update": false
            }
        }


class UploadLawsRequest(BaseModel):
    """Upload internal laws metadata schema."""
    
    file_name: str = Field(..., description="Uploaded file name")
    file_type: str = Field(..., description="File type (PDF/DOCX)")
    description: Optional[str] = Field(None, max_length=500, description="File description")
    category: Optional[str] = Field(None, description="Law category")
    
    class Config:
        schema_extra = {
            "example": {
                "file_name": "company_internal_policy.pdf",
                "file_type": "PDF",
                "description": "Internal company policies and procedures",
                "category": "internal_policies"
            }
        }


class AdminAgentCommand(BaseModel):
    """Admin agent command schema."""
    
    command: str = Field(..., min_length=1, max_length=1000, description="Admin command")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Command context")
    
    @validator('command')
    def validate_command(cls, v):
        if not v.strip():
            raise ValueError('Command cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "command": "Generate statistics for this month",
                "context": {"format": "excel"}
            }
        }


class AdminAgentResponse(BaseModel):
    """Admin agent response schema."""
    
    response: str = Field(..., description="Agent response")
    action_taken: Optional[str] = Field(None, description="Action performed")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response data")
    success: bool = Field(..., description="Command success status")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Statistics report generated successfully for January 2024",
                "action_taken": "generate_report",
                "data": {
                    "report_url": "/reports/stats_2024_01.xlsx",
                    "total_users": 150,
                    "total_chats": 1250
                },
                "success": true
            }
        }


class UserManagementRequest(BaseModel):
    """User management request schema."""
    
    email: str = Field(..., description="Target user email")
    action: str = Field(..., description="Action to perform")
    reason: Optional[str] = Field(None, description="Action reason")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ["activate", "deactivate", "query", "delete"]
        if v not in valid_actions:
            raise ValueError(f'Invalid action: {v}. Valid actions: {valid_actions}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "action": "deactivate",
                "reason": "Violation of terms of service"
            }
        }


class AdminStatsResponse(BaseModel):
    """Admin statistics response schema."""
    
    total_users: int = Field(..., description="Total user count")
    active_users: int = Field(..., description="Active user count")
    total_sessions: int = Field(..., description="Total session count")
    active_sessions: int = Field(..., description="Active session count")
    total_messages: int = Field(..., description="Total message count")
    messages_today: int = Field(..., description="Messages sent today")
    seven_day_activity: List[Dict[str, Any]] = Field(..., description="7-day activity data")
    storage_stats: Dict[str, Any] = Field(..., description="Storage statistics")
    
    class Config:
        schema_extra = {
            "example": {
                "total_users": 150,
                "active_users": 120,
                "total_sessions": 1250,
                "active_sessions": 45,
                "total_messages": 15000,
                "messages_today": 350,
                "seven_day_activity": [
                    {"date": "2024-01-01", "users": 45, "messages": 350},
                    {"date": "2024-01-02", "users": 52, "messages": 420}
                ],
                "storage_stats": {
                    "mongodb_size": "150MB",
                    "milvus_vectors": 25000,
                    "uploaded_files": "2.5GB"
                }
            }
        }


class AdminLogResponse(BaseModel):
    """Admin log response schema."""
    
    id: str = Field(..., description="Log ID")
    admin_email: str = Field(..., description="Admin email")
    action: AdminAction = Field(..., description="Action performed")
    params: Dict[str, Any] = Field(..., description="Action parameters")
    result: Dict[str, Any] = Field(..., description="Action result")
    success: bool = Field(..., description="Success status")
    execution_time: Optional[float] = Field(None, description="Execution time")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439013",
                "admin_email": "admin@example.com",
                "action": "crawl_laws",
                "params": {"law_types": ["enterprises"]},
                "result": {"documents_processed": 150},
                "success": true,
                "execution_time": 45.2,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
