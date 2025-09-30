"""
Core configuration management for EasyLaw application.
Handles environment-specific settings for dev/prod environments.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App Configuration
    app_name: str = Field(default="EasyLaw", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="debug", env="LOG_LEVEL")
    
    # Server Configuration
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Database Configuration
    mongodb_uri: str = Field(env="MONGODB_URI")
    mongodb_db_name: str = Field(env="MONGODB_DB_NAME")
    
    # Milvus Configuration
    milvus_uri: str = Field(env="MILVUS_URI")
    milvus_user: Optional[str] = Field(default=None, env="MILVUS_USER")
    milvus_password: Optional[str] = Field(default=None, env="MILVUS_PASSWORD")
    milvus_db_name: str = Field(env="MILVUS_DB_NAME")
    
    # AI Configuration
    gemini_api_key: str = Field(env="GEMINI_API_KEY")
    embedding_model: str = Field(default="models/embedding-001", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="gemini-1.5-pro", env="LLM_MODEL")
    max_tokens: int = Field(default=4096, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    # Authentication
    jwt_secret: str = Field(env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, env="JWT_EXPIRE_MINUTES")
    
    # Admin Configuration
    admin_email: str = Field(env="ADMIN_EMAIL")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    
    # File Upload
    max_file_size: str = Field(default="50MB", env="MAX_FILE_SIZE")
    upload_folder: str = Field(default="./uploads", env="UPLOAD_FOLDER")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Chat Configuration
    max_active_sessions: int = Field(default=3, env="MAX_ACTIVE_SESSIONS")
    chat_history_limit: int = Field(default=50, env="CHAT_HISTORY_LIMIT")
    context_window_size: int = Field(default=4000, env="CONTEXT_WINDOW_SIZE")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    env_file = os.getenv("ENV_FILE", ".env.dev")
    return Settings(_env_file=env_file)


# Global settings instance
settings = get_settings()
