"""
API schemas for EasyLaw application.
"""

from .auth import (
    UserRegistration,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordReset,
    PasswordChange
)
from .chat import (
    SessionCreate,
    SessionResponse,
    MessageCreate,
    MessageResponse,
    ChatHistoryResponse,
    SessionsListResponse,
    StreamingResponse
)
from .admin import (
    CrawlLawsRequest,
    UploadLawsRequest,
    AdminAgentCommand,
    AdminAgentResponse,
    UserManagementRequest,
    AdminStatsResponse,
    AdminLogResponse
)

__all__ = [
    # Auth schemas
    "UserRegistration",
    "UserLogin",
    "UserResponse", 
    "TokenResponse",
    "PasswordReset",
    "PasswordChange",
    
    # Chat schemas
    "SessionCreate",
    "SessionResponse",
    "MessageCreate",
    "MessageResponse",
    "ChatHistoryResponse",
    "SessionsListResponse",
    "StreamingResponse",
    
    # Admin schemas
    "CrawlLawsRequest",
    "UploadLawsRequest",
    "AdminAgentCommand",
    "AdminAgentResponse",
    "UserManagementRequest",
    "AdminStatsResponse",
    "AdminLogResponse"
]
