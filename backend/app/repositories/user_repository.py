"""
User repository for MongoDB operations.
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import motor.motor_asyncio

from ..models.user import User, UserInDB, UserRole, UserStatus
from ..core.config import settings
from ..core.exceptions import NotFoundError, ConflictError


class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
        self.database = self.client[settings.mongodb_db_name]
        self.collection = self.database.users
    
    async def create_user(self, user_data: dict) -> UserInDB:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data["email"])
        if existing_user:
            raise ConflictError(f"User with email {user_data['email']} already exists")
        
        # Prepare user document
        user_doc = {
            "email": user_data["email"],
            "password_hash": user_data["password_hash"],
            "role": user_data.get("role", UserRole.USER.value),
            "status": user_data.get("status", UserStatus.ACTIVE.value),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "login_count": 0
        }
        
        # Insert user
        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return UserInDB(**user_doc)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        try:
            object_id = ObjectId(user_id)
            user_doc = await self.collection.find_one({"_id": object_id})
            
            if user_doc:
                return UserInDB(**user_doc)
            return None
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        user_doc = await self.collection.find_one({"email": email})
        
        if user_doc:
            return UserInDB(**user_doc)
        return None
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[UserInDB]:
        """Update user information."""
        try:
            object_id = ObjectId(user_id)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update user
            result = await self.collection.find_one_and_update(
                {"_id": object_id},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                return UserInDB(**result)
            return None
        except Exception:
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            object_id = ObjectId(user_id)
            
            result = await self.collection.update_one(
                {"_id": object_id},
                {
                    "$set": {
                        "last_login": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"login_count": 1}
                }
            )
            
            return result.modified_count > 0
        except Exception:
            return False
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        result = await self.update_user(user_id, {"status": UserStatus.INACTIVE.value})
        return result is not None
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        result = await self.update_user(user_id, {"status": UserStatus.ACTIVE.value})
        return result is not None
    
    async def change_password(self, user_id: str, new_password_hash: str) -> bool:
        """Change user password."""
        result = await self.update_user(user_id, {"password_hash": new_password_hash})
        return result is not None
    
    async def get_all_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[UserInDB]:
        """Get all users with pagination."""
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        users = []
        
        async for user_doc in cursor:
            users.append(UserInDB(**user_doc))
        
        return users
    
    async def get_user_count(self, status_filter: Optional[str] = None) -> int:
        """Get total user count."""
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        return await self.collection.count_documents(query)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user (admin only operation)."""
        try:
            object_id = ObjectId(user_id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def get_admin_users(self) -> List[UserInDB]:
        """Get all admin users."""
        cursor = self.collection.find({"role": UserRole.ADMIN.value})
        admins = []
        
        async for user_doc in cursor:
            admins.append(UserInDB(**user_doc))
        
        return admins
    
    async def create_admin_user(self, email: str, password_hash: str) -> UserInDB:
        """Create admin user."""
        admin_data = {
            "email": email,
            "password_hash": password_hash,
            "role": UserRole.ADMIN.value,
            "status": UserStatus.ACTIVE.value
        }
        
        return await self.create_user(admin_data)
    
    async def ensure_admin_exists(self) -> UserInDB:
        """Ensure admin user exists, create if not."""
        admin_email = settings.admin_email
        admin_user = await self.get_user_by_email(admin_email)
        
        if not admin_user:
            # Create default admin user
            from ..core.security import security
            default_password = "admin123"  # TODO: Change this in production
            password_hash = security.hash_password(default_password)
            
            admin_user = await self.create_admin_user(admin_email, password_hash)
        
        return admin_user
