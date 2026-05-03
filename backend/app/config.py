import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: Optional[str] = os.getenv("LLM_BASE_URL")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Embedding Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    EMBEDDING_API_KEY: Optional[str] = os.getenv("EMBEDDING_API_KEY")
    EMBEDDING_BASE_URL: Optional[str] = os.getenv("EMBEDDING_BASE_URL")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    # Vector Store Settings
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "chroma")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # RAG Settings
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_SCORE_THRESHOLD: float = float(os.getenv("RAG_SCORE_THRESHOLD", "0.7"))
    RAG_MAX_CONTEXT_LENGTH: int = int(os.getenv("RAG_MAX_CONTEXT_LENGTH", "4000"))

    # CORS Settings
    CORS_ALLOW_ORIGINS: str = os.getenv("CORS_ALLOW_ORIGINS", "*")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"


settings = Settings()