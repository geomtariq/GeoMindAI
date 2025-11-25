from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
import os
from dotenv import load_dotenv

# Force load .env file to override any stale environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path, override=True)

class Settings(BaseSettings):
    USE_MOCK_DB: bool = False
    GEMINI_API_KEY: str | None = None  # Optional, falls back to mock if not set
    
    @field_validator('USE_MOCK_DB', mode='before')
    @classmethod
    def parse_bool(cls, v):
        """Handle string boolean values from environment variables"""
        if isinstance(v, str):
            v = v.strip()  # Remove trailing spaces
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields instead of raising error
    )

settings = Settings()
