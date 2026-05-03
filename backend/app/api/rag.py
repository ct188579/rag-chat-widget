from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List

from app.services.rag_engine import RAGEngine
from app.core.vector_store import VectorStore
from app.core.llm import LLMManager

router = APIRouter()


def get_vector_store(http_request: Request):
    return http_request.app.state.vector_store


def get_llm_manager(http_request: Request):
    return http_request.app.state.llm_manager


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    namespace: Optional[str] = None
    score_threshold: float = 0.7


class SearchResponse(BaseModel):
    sources: List[dict]
    query: str


class NamespaceResponse(BaseModel):
    namespace: str
    document_count: int


@router.post("/search", response_model=SearchResponse)
async def search_documents(
        request: SearchRequest,
        vector_store: VectorStore = Depends(get_vector_store),
        llm: LLMManager = Depends(get_llm_manager)
):
    """搜索相关文档"""
    try:
        rag_engine = RAGEngine(vector_store, llm)
        sources = await rag_engine.retrieve(
            query=request.query,
            top_k=request.top_k,
            namespace=request.namespace,
            score_threshold=request.score_threshold
        )
        
        return SearchResponse(
            query=request.query,
            sources=[s.dict() for s in sources]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespaces", response_model=List[NamespaceResponse])
async def list_namespaces(request):
    """列出所有命名空间"""
    return []


@router.delete("/namespaces/{namespace}")
async def delete_namespace(namespace: str, request):
    """删除命名空间下的所有文档"""
    try:
        vector_store = request.app.state.vector_store
        await vector_store.delete_namespace(namespace)
        return {"status": "success", "namespace": namespace}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))