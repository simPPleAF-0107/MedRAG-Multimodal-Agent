import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env is loaded strictly into os.environ for external libraries (HuggingFace, etc.)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

# ── Force HuggingFace cache into project folder (must be set BEFORE HF imports) ──
_project_root = os.path.dirname(os.path.dirname(__file__))
_hf_cache = os.path.join(_project_root, "models", "huggingface")
os.makedirs(_hf_cache, exist_ok=True)
os.environ.setdefault("HF_HOME", _hf_cache)
os.environ.setdefault("HF_DATASETS_CACHE", os.path.join(_hf_cache, "datasets"))
os.environ.setdefault("TRANSFORMERS_CACHE", os.path.join(_hf_cache, "hub"))
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", os.path.join(_hf_cache, "hub"))

class Settings(BaseSettings):
    """
    Core application settings loaded from environment variables.
    """
    # API Configuration
    PROJECT_NAME: str = "MedRAG Multimodal Agent"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # JWT Configuration
    SECRET_KEY: str = "yoursecretkey_medrag_multimodal_agent_2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    # OpenAI Configuration
    OPENAI_API_KEY: str = ""

    # Vector DB Configuration
    QDRANT_DB_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector-db")
    TEXT_EMBEDDING_MODEL: str = "all-mpnet-base-v2"
    IMAGE_EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"  # Example CLIP model

    # SQLite Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./medrag.db"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
