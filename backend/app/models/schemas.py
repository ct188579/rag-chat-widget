from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RAGSource(BaseModel):
    id: str
    title: str
    content: str
    score: float
    url: Optional[str] = None
    page: Optional[int] = None


class RAGConfig(BaseModel):
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.7, ge=0, le=1)
    namespace: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = ""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    enable_rag: bool = True
    rag_config: Optional[RAGConfig] = None
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[RAGSource] = []
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentUpload(BaseModel):
    title: str
    namespace: Optional[str] = "default"
    metadata: Optional[Dict[str, Any]] = None