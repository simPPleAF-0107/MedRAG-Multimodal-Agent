import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Core application settings loaded from environment variables.
    """
    # API Configuration
    PROJECT_NAME: str = "MedRAG Multimodal Agent"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # OpenAI Configuration
    OPENAI_API_KEY: str

    # Vector DB Configuration
    CHROMA_DB_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector-db")
    TEXT_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    IMAGE_EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"  # Example CLIP model

    # SQLite Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./medrag.db"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
